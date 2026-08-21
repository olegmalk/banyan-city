#!/usr/bin/env python3
r"""THE FOUNDER'S BEAT-BY-BEAT NOTES OF 2026-08-21 NIGHT, TURNED INTO THREE JOBS.

    python3 pipeline/file_beatfix_0822.py            # dry run
    python3 pipeline/file_beatfix_0822.py --write

HIS WORDS, VERBATIM, ONE PER BEAT
--------------------------------------------------------------------------
b01  "not bad, its alright, the only small problem i see is the fig. its
      basically just a ball with a simple stick poking out the top, and
      also.. for some reason it changes colors, from green to purple."
b02  "the goblin looks too serious the whole time, like a soldier. and also
      he just faceplants into the ground."
b03  "wouldn't be that bad, if the goblin didn't look like an old man."
b04  "also wouldn't be bad if he didnt look so chibi in this."

Beat 04 is NOT in this file and that is deliberate: the fix he is asking for
already exists in rendered pixels (`ep2-b04-canonmotion-0821`, 6 of 7, his own
design), so it is a staging job and not a render one. Spending the card on a
beat that is already right would be the expensive way to say nothing.

WHAT EACH JOB CHANGES, AND WHY THAT IS THE CHEAPEST LEVER THAT CAN WORK
--------------------------------------------------------------------------
BEAT 01 -- THE FIG'S SHAPE, THROUGH WORDING, AND THE COLOUR IS LEFT ALONE.
  The colour flip is NOT a defect. The approved script (node 002b, live leaf
  002b-t0-c) says of the cold open: "a green nub swells, darkens and rounds
  into a single fig". Green to purple IS the ripening, it is the only event in
  the beat, and re-rendering it out would be re-writing his script on a note
  that reads as a question. It is answered on the page instead, with the line
  quoted, and left in the picture.
  The SHAPE half is a defect and its cause is sitting in the prompt: the
  shipped take's motion prompt says the nub "swells, darkens and ROUNDS into a
  single deep purple fig". The instruction asks for a ball and the model drew
  one. Nothing in that prompt or its negative says what a fig looks like. So
  the first rung is the wording -- one clause of silhouette, and the ball terms
  banned -- on the SAME plate and the SAME recipe. If the wording will not bind
  the shape, the next rung is the composite (fig-silhouette nub instead of the
  ellipse `nub_composite.py` draws today), and that is written down in
  `next_rung_if_this_fails` rather than fired blind alongside it.

BEAT 02 -- THE EXPRESSION, IN THE PIXELS, BECAUSE THE PROMPT WAS MEASURED
  REFUSING IT. This lane does not get to re-discover that. `ep2-jerry-expref-
  r2-0821` established it on this exact recipe: expression is not reachable
  from the prompt -- s1, m1 (mask fitted to the head), m2 (ip-scale 0.7 to
  0.45) and e1 (expression tags dropped) all came back with the same face, and
  Option B wore it with no expression tags at all. What moved it was repainting
  the brow and mouth bands of the REFERENCE. So the panic goes into the plate
  the same way, by a masked i2i over two bands of the canon plate's face, and
  the motion prompt's existing "his face DOES NOT CHANGE" clause then carries
  it for 105 frames -- which is the one thing round 2 proved that clause does
  reliably (R4 PASS, features drawn in every frame, no dissolve).
  THE EYES ARE NOT IN THE MASK. The slit pupil is the identity clause this
  character is most often losing, and the mood is not in it.
  The faceplant is the second half of his note and it is an ACTION-WORDING
  change on the same job: round 2's own verdict says the plate fixed the camera
  and left "the SHAPE of the move" wrong -- "there is no entry, no skid, and
  the dive reads as a duck". The landing is now written as a placement, not an
  adjective: forearms take it, chin off the ground, head up at the end.

BEAT 03 -- MOTION ONLY, BECAUSE THE DESIGN HE IS OBJECTING TO IS ALREADY FIXED
  IN A CLIP HE HAS NOT SEEN. "Looks like an old man" is the shipped take's
  fault, and the audit agrees with him in the same words (human nose with
  nostrils, rounded human ear, folds either side of the mouth). The canon-
  motion round 2 clip drew his own tile's face instead and its verdict is
  explicit: horn gone, identity PASS in all 105 frames, trunk present and
  unmoved. Its ONE fault is that nothing happens -- "a still with a runtime",
  the degenerate outcome that job pre-registered by name and then hit. So the
  design does not need another round; the action does. Same plate, same
  recipe, same everything, and the action re-written as three head-and-
  shoulder moves with a start, a middle and an end instead of "hold still",
  which is what a motion model was asked for and correctly declined to invent.

WHAT DOES NOT MOVE IN ANY OF THE THREE: size, frame count, fps, guidance,
sampler, sigmas, two-stage, crf, offload, the cover-crop sha assert. Seeds move
because a re-run on an identical seed and an identical prompt is a copy.

NOTHING HERE TOUCHES review/ep2-ship-0821. Every output is a CANDIDATE staged
on review/ep2-beats-0821 for his pick. No cut swaps -- his 08-21 ruling.
"""
import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77     # noqa: E402

import yaml as _yaml                                          # noqa: E402

BOXPY = r"C:\banyan-farm\venv\Scripts\python.exe"

# --------------------------------------------------------------------------
# BEAT 01 -- the fig's silhouette, said in words for the first time.
# --------------------------------------------------------------------------
B01_PROMPT = (
    "On the thinnest branch of the tiny two-leaf sapling, the small green nub "
    "swells and darkens into a single ripe fig. THE FIG'S SHAPE: a teardrop -- "
    "wide, heavy and rounded at the BOTTOM, tapering upward to a short thick "
    "neck where it meets the branch, like a small pear hanging point-up. It is "
    "not a sphere and there is no bare stalk showing above it. It is the only "
    "thing in frame that moves. Detailed cinematic anime, warm amber "
    "backlight, hazy out-of-focus grassy field, soft glowing light, "
    "masterpiece, best quality, very aesthetic.")

B01_NEGATIVE = (
    "round ball, sphere, spherical fruit, perfect circle, berry, cherry, "
    "grape, apple, lollipop, ball on a stick, bare thin stalk, long stem, "
    "pin, antenna, camera pan, camera tilt, zoom, dolly, push in, pull back, "
    "tripod, cut to another shot, scene change, different location, split "
    "screen, still image, freeze frame, growing plant, sprouting, unfurling "
    "leaves, stem lengthening, leaves enlarging, plant enlarging, blooming, "
    "brightening, exposure change, overexposed, blown highlights, changing "
    "background")

# --------------------------------------------------------------------------
# BEAT 02 -- the panic goes into the plate; the landing goes into the action.
# --------------------------------------------------------------------------
B02_PLATE = (r"C:\banyan-farm\courier-box\farm-out\ep2-b02-sapnat-0821"
             r"\b02-sapnat-s20260820.png")
B02_PLATE_REL = "farm-out/ep2-b02-sapnat-0821/b02-sapnat-s20260820.png"
B02_PLATE_SHA = ("30dce0fabd444fdf5e0727eb4c6a317d65004f71a7df0dbe5cb126224db"
                 "f46ea")

# Measured off the plate at 1:1, drawn as an overlay and looked at before this
# file was written. The plate is 832x1216 and his head fills the top third, so
# the two bands are large enough for the i2i to have somewhere to work.
#   BROW  268,90  -> 604,166   both eyebrows and the forehead above them.
#                              Bottom edge stops 11 px above the eye line.
#   MOUTH 334,274 -> 506,350   the mouth and the jaw around it. Top edge is
#                              14 px below the nose, bottom edge is above the
#                              collar.
# THE EYES (roughly y 177-268) ARE IN NEITHER BAND, on purpose.
B02_BROW = (268, 90, 604, 166)
B02_MOUTH = (334, 274, 506, 350)

B02_FACE_PROMPT = (
    "masterpiece, best quality, very aesthetic, green skin goblin face, "
    "eyebrows raised high and arched, wide open mouth, shouting, gasping, "
    "panicked, terrified, running for his life")

B02_FACE_NEGATIVE = (
    "lowres, worst quality, low quality, calm, neutral, blank expression, "
    "stern, serious, stoic, soldier, closed mouth, frown, angry, scowl, "
    "furrowed brow, teeth, tongue, human face, human nose, beard, wrinkles, "
    "old man, text, watermark")

B02_ACTION = (
    "THE ACTION: he runs in from the left, skids on one foot, and throws "
    "himself down flat behind the sapling stem that is already there -- entry, "
    "skid, dive, in that order, as one continuous move. HE DOES NOT LAND ON "
    "HIS FACE: his forearms take the landing, his chin stays off the ground, "
    "and he ends LYING PRONE ON HIS CHEST behind the stem with his head raised "
    "and his eyes forward. His mouth stays wide open and his brows stay high "
    "the whole time. HALFWAY THROUGH he is mid-skid, still upright, leaning "
    "back, not yet down.")

B02_NEGATIVE_EXTRA = (
    ", face down, face in the dirt, head flat on the ground, lying on his "
    "back, kneeling, standing still, calm face, closed mouth")

# --------------------------------------------------------------------------
# BEAT 03 -- the same picture, given something to do.
# --------------------------------------------------------------------------
B03_ACTION = (
    "THE ACTION: three separate moves, one after the other, and he is still "
    "moving when the clip ends. FIRST he drops his head and shoulders down and "
    "sideways behind the thin stem that is already there, hunching until his "
    "shoulders are up around his ears. THEN his head comes back up and turns "
    "to look off to his left, away from the stem. THEN it snaps back to "
    "centre. His body stays where it is and only his head, neck and shoulders "
    "travel. HALFWAY THROUGH his head is at its lowest, tucked down and "
    "tilted, shoulders hunched up around it.")


def head_of(prompt: str) -> str:
    """Everything before THE ACTION -- the identity clause and the inventory
    of what is already in the picture. Carried BYTE-FOR-BYTE: round 2 measured
    it holding the face for all 105 frames on both of these beats (R4 PASS),
    and the founder's notes are not about the face's canon, they are about
    what it is DOING."""
    return prompt[:prompt.index("THE ACTION:")].rstrip()


def sha_of(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def b02_plate_steps(child: dict) -> None:
    """THE REPAINT IS ITS OWN JOB, AND box_enqueue IS RIGHT TO INSIST.

    The first shape of this was one job -- repaint, then crop, then render --
    and the queue refused it twice, correctly: its crop step's `--src` was a
    file that would not exist until three steps in, so neither the plate guard
    (fetch the picture and look at it) nor the refs guard (which job drew it?)
    could check anything, and 'could not check' is not 'fine'. A `plate_ack:`
    waiver would have silenced both.

    Splitting it costs one round trip and buys two things the waiver would
    have thrown away: the guards get a real farm-out directory to read, and
    THE PLATE GETS LOOKED AT BEFORE EIGHT GPU-MINUTES ARE SPENT ANIMATING IT,
    which is the one-sample rule this repo keeps re-learning.
    """
    root = r"C:\banyan-farm\b02panicface-0822"
    mask = root + r"\b02-panic-mask.png"
    plate = root + r"\b02-panic-plate.png"

    mask_code = (
        "# The mask is BUILT HERE, not shipped as a blob, so the two bands are\n"
        "# readable as numbers in the spec that a reviewer can check against\n"
        "# the plate. No model, no network, no GPU.\n"
        "from PIL import Image, ImageDraw\n"
        "import os\n"
        "root = r'%s'\n"
        "os.makedirs(root, exist_ok=True)\n"
        "m = Image.new('L', (832, 1216), 0)\n"
        "d = ImageDraw.Draw(m)\n"
        "d.rectangle([%d, %d, %d, %d], fill=255)   # BROW band\n"
        "d.rectangle([%d, %d, %d, %d], fill=255)   # MOUTH band\n"
        "out = os.path.join(root, 'b02-panic-mask.png')\n"
        "m.save(out)\n"
        "print('mask 832x1216 ->', out)\n"
        "print('brow  %s')\n"
        "print('mouth %s')\n"
        "print('THE EYES (about y 177-268) ARE IN NEITHER BAND.')\n"
        % (root, B02_BROW[0], B02_BROW[1], B02_BROW[2], B02_BROW[3],
           B02_MOUTH[0], B02_MOUTH[1], B02_MOUTH[2], B02_MOUTH[3],
           str(list(B02_BROW)), str(list(B02_MOUTH))))

    face_note = (
        "THE PANIC GOES IN AS PIXELS. Strength 0.42 over two bands of the "
        "canon plate's face -- brow and mouth -- with the eyes outside the "
        "mask. ep2-jerry-expref-r2-0821 measured that expression does not "
        "bind through the prompt on this recipe (four interventions, same "
        "face every time) and that repainting these same two bands is what "
        "moved it. 0.42 sits in the band this repo has measured preserving "
        "layout and identity while still redrawing what is inside the mask.")

    publish_code = (
        "# EVERY FILE IS NAMED IN FULL, not matched by a glob, and the exit\n"
        "# code asserts the count -- the parent spec's own rule, kept.\n"
        "# THE MASK AND THE PROMPTS TRAVEL WITH THE PLATE: a reader scoring\n"
        "# whether the expression moved needs the hole it was painted through.\n"
        "import hashlib, os, shutil\n"
        "from_dir = 'C:/banyan-farm/b02panicface-0822'\n"
        "dst = 'C:/banyan-farm/courier-box/farm-out/ep2-b02-panicface-0822'\n"
        "NAMES = ['b02-panic-plate.png', 'b02-panic-plate.png.meta.yaml',\n"
        "         'b02-panic-mask.png', 'b02-face-prompt.txt',\n"
        "         'b02-face-negative.txt']\n"
        "os.makedirs(dst, exist_ok=True)\n"
        "lines = []\n"
        "for name in NAMES:\n"
        "    f = os.path.join(from_dir, name)\n"
        "    if not os.path.isfile(f):\n"
        "        raise SystemExit('!! missing %s -- refusing to call the job "
        "clean.' % f)\n"
        "    shutil.copy2(f, dst)\n"
        "    with open(os.path.join(dst, name), 'rb') as fh:\n"
        "        lines.append(hashlib.sha256(fh.read()).hexdigest() + '  ' + name)\n"
        "with open(os.path.join(dst, 'ep2-b02-panicface-0822.sha256'), 'w',\n"
        "          newline='\\n') as fh:\n"
        "    fh.write('\\n'.join(sorted(lines)) + '\\n')\n"
        "print('published', len(lines), 'file(s) + manifest ->', dst)\n"
        "raise SystemExit(0 if len(lines) == len(NAMES) else 1)\n")

    child["steps"] = [
        {"name": "mask", "argv": [BOXPY, "-c", mask_code]},
        {"name": "dry", "argv": [
            BOXPY, root + r"\inpaint_fruit.py",
            "--init", B02_PLATE, "--init-sha256", B02_PLATE_SHA,
            "--mask-png", mask,
            "--prompt-file", root + r"\b02-face-prompt.txt",
            "--negative-file", root + r"\b02-face-negative.txt",
            "--out", root + r"\b02-panic-DRY.png",
            "--steps", "40", "--cfg", "7.5", "--strength", "0.42",
            "--pad-crop", "64", "--blur", "8", "--seed", "20260822",
            "--note", "MASK GEOMETRY CHECK. Asserts the plate's digest and "
                      "resolves the mask BEFORE a model loads, so wrong bands "
                      "cost seconds instead of a GPU fire.",
            "--dry-run"]},
        {"name": "face", "argv": [
            BOXPY, root + r"\inpaint_fruit.py",
            "--init", B02_PLATE,
            "--init-sha256", B02_PLATE_SHA,
            "--mask-png", mask,
            "--prompt-file", root + r"\b02-face-prompt.txt",
            "--negative-file", root + r"\b02-face-negative.txt",
            "--out", plate,
            "--steps", "40", "--cfg", "7.5", "--strength", "0.42",
            "--pad-crop", "64", "--blur", "8", "--seed", "20260822",
            "--note", face_note]},
        {"name": "publish", "argv": [BOXPY, "-c", publish_code]},
    ]
    child["artifacts"] = [plate]

    # inpaint_fruit.py is already the parent's payload and travels unchanged;
    # its fetch helper is not needed here and would otherwise ship dead.
    for key in list(child["payload"]):
        if key.endswith("fetch_init.py"):
            del child["payload"][key]
    child["payload"][root + r"\b02-face-prompt.txt"] = B02_FACE_PROMPT
    child["payload"][root + r"\b02-face-negative.txt"] = B02_FACE_NEGATIVE
    for key in list(child["payload"]):
        base = key.rsplit("\\", 1)[-1]
        if base in ("prompt.txt", "negative.txt"):
            del child["payload"][key]


ROWS = [
    {
        "beat": 1,
        "parent": "pipeline/jobs/ep2-b01-fignonly-s20260871-0821.yaml",
        "new_id": "ep2-b01-figshape-0822",
        "retoken": [("fignonly-s20260871-0821", "figshape-0822")],
        "seed": 20260822,
        "est": 12,
        "overrides": {
            "payload:b01-motion-prompt.txt": B01_PROMPT,
            "payload:b01-negative.txt": B01_NEGATIVE,
        },
        "fresh": {
            "owner": "the per-beat iteration lane, 2026-08-22",
            "consumer":
                "A CANDIDATE for beat 01 on review/ep2-beats-0821, answering "
                "the shape half of the founder's 2026-08-21 note. It is staged "
                "beside the take that is in the cut so he picks between two "
                "finished clips; review/ep2-ship-0821 is not touched and no "
                "cut moves because this landed.",
            "success":
                "ONE 704x1280 121-frame 24fps mp4 in which the fruit reads as "
                "a FIG. S1 at the last frame the fruit is wider across its "
                "bottom half than its top half -- a teardrop, not a disc; S2 "
                "no bare stalk stands clear above it, so the silhouette is "
                "fruit-then-branch and not ball-on-a-stick; S3 the growth is "
                "still continuous and still the only thing moving, which the "
                "shipped take passes and this must not lose; S4 the field is "
                "no worse than the shipped take's -- that beat's standing "
                "G5a fault is NOT in scope here and a job that fixed it by "
                "accident would still be judged on S1-S3.",
            "why":
                "THE INSTRUCTION ASKED FOR A BALL. The shipped take's motion "
                "prompt reads 'the small green nub swells, darkens and ROUNDS "
                "into a single deep purple fig', and neither it nor its "
                "negative says anything else about the shape. The founder's "
                "note is 'its basically just a ball with a simple stick "
                "poking out the top'. That is the prompt's own word coming "
                "back. So the first rung is the wording: one clause of "
                "silhouette in the positive, the ball vocabulary in the "
                "negative, SAME plate, SAME recipe, SAME everything else. "
                "THE COLOUR HALF OF HIS NOTE IS NOT ACTED ON, and that is a "
                "decision with a citation rather than an omission: the "
                "approved script says 'a green nub swells, darkens and rounds "
                "into a single fig', so green-to-purple is the ripening the "
                "beat exists to show. It is answered on the page in his own "
                "script's words and left in the picture.",
        },
        "extra": {
            "the_one_variable":
                "THE WORDING, and nothing else. Same init plate "
                "(b01-nubcomp-s20260826.png, sha 1b6d3492..), same 704x1280, "
                "same 121 frames at 24fps, same guidance 2.0, same distilled "
                "sigmas, same two-stage, same crf 33, same offload. The seed "
                "moves because a re-run at an identical seed and an identical "
                "prompt is a copy, not a rung.",
            "colour_is_canon_and_is_deliberately_left_alone":
                "Node 002b-first-citizen, live leaf 002b-t0-c, COLD OPEN: 'A "
                "tiny two-leaf banyan sapling in a green field. On the "
                "thinnest branch a green nub swells, darkens and rounds into "
                "a single fig -- the only thing in frame that moves.' The "
                "colour change IS the beat. Beat 20's fig was corrected TO "
                "purple on the same canon. A lane that quietly froze the "
                "colour here would be re-writing an approved script on the "
                "strength of a note that reads as a question, which is a "
                "taste call and not this lane's (R4).",
            "next_rung_if_this_fails":
                "THE COMPOSITE, not more words. pipeline/nub_composite.py "
                "draws the frame-1 nub as an ELLIPSE (--radii 10,13) and the "
                "0.30 naturalise then shades whatever shape it finds. If the "
                "silhouette clause does not bind, the fix is a fig-shaped "
                "alpha in that tool -- broad at the bottom, necked at the "
                "top -- on the ep2-b01-compseed-s3-g5-0818 plate, which is "
                "the same structural-first pattern that had to be used for "
                "the fruit's COLOUR when the prompt route failed there. It is "
                "written here and NOT fired alongside this one, because two "
                "levers in one round cannot tell you which one worked.",
            "failure_predicted_in_advance":
                "THE SILHOUETTE WORDS COST MOTION. This beat's whole content "
                "is one small growth and the shipped take already reaches 90% "
                "of it late (f108). A long shape clause competes for the same "
                "budget as the growth verb, and the plausible failure is a "
                "correctly-shaped fig that barely changes size. S3 is what "
                "catches it. SECOND: the ban list contains 'sphere' and "
                "'perfect circle' -- if the model reads those as a ban on "
                "roundness generally, the fruit can come back lumpy.",
        },
    },
    {
        "beat": 2,
        "parent": "pipeline/jobs/ep2-b02-sapnat-0821.yaml",
        "new_id": "ep2-b02-panicface-0822",
        "retoken": [("b02sapnat-0821", "b02panicface-0822")],
        "seed": 20260822,
        "est": 4,
        "post": b02_plate_steps,
        "overrides": {},
        "fresh": {
            "owner": "the per-beat iteration lane, 2026-08-22",
            "consumer":
                "THE PLATE beat 02's next motion round runs on, and nothing "
                "else. It is looked at at 1:1 first; only then is the motion "
                "job filed against it. review/ep2-ship-0821 is not touched by "
                "this job and no clip changes because it landed.",
            "success":
                "ONE 832x1216 png that is the same creature with a different "
                "MOOD. F1 the brows are up and arched and the mouth is open "
                "wide -- panic, not the flat soldier's line the founder "
                "named; F2 the eyes are BYTE-IDENTICAL to the source plate, "
                "because they are outside the mask, and the slit pupils are "
                "still slit pupils; F3 nothing outside the two bands moved -- "
                "ears, skull, collar, shirt, the composited sapling and the "
                "grass are the source plate's; F4 no human brow ridge, no "
                "hairline, no teeth, no nose change. THIS JOB DECIDES "
                "NOTHING: if F1 fails the strength moves, if F2 or F3 fail "
                "the bands move, and no GPU-minute goes on motion either way.",
            "why":
                "HALF OF THE FOUNDER'S BEAT-02 NOTE IS A FACE, AND ON THIS "
                "RECIPE A FACE IS PIXELS, NOT WORDS. The landing half of his "
                "note is an action-wording change and it rides on the motion "
                "job that runs after this plate is looked at; this job is "
                "only the face.\n\nTHE FACE. 'Too serious the "
                "whole time, like a soldier.' Expression is NOT reachable "
                "from the prompt on this recipe and that is measured, not "
                "assumed: ep2-jerry-expref-r2-0821 moved the mask, the "
                "adapter scale and the expression tags -- four interventions, "
                "MAE 28.4/24.0/7.9 between them so they were real -- and the "
                "face did not change, while a version carrying NO expression "
                "tags at all wore the same one. What did move it was "
                "repainting the brow and mouth bands of the reference. So the "
                "panic is painted into the plate here, over exactly those two "
                "bands, with the eyes left outside the mask because the slit "
                "pupil is the identity clause this character loses most "
                "often. The motion prompt's existing 'his face DOES NOT "
                "CHANGE' clause then carries it for 105 frames, which is the "
                "one thing round 2 proved that clause does reliably (R4 PASS, "
                "features drawn in all 105 frames, no dissolve).\n\nWHAT DID "
                "NOT CHANGE FROM THE PARENT: the same masked-i2i tool, the "
                "same 40 steps, the same cfg 7.5, the same pad-crop 64 and "
                "blur 8, the same publish-by-name discipline. The strength "
                "goes 0.30 -> 0.42 because the parent was FINISHING a shape "
                "that had been composited in and this has to REPLACE the "
                "shapes it finds; 0.42 is still inside the band this repo has "
                "measured preserving layout and identity.",
        },
        "extra": {
            "the_one_variable":
                "THE FACE'S MOOD, painted into two bands of one plate. "
                "Everything else about the plate is the source plate's, and "
                "the eyes are not even in the mask. The action wording is a "
                "SEPARATE change on a SEPARATE job, so a mixed result stays "
                "readable: if the motion round comes back panicked but "
                "face-planting, the face lever worked and the landing lever "
                "did not.",
            "the_mask_geometry_was_looked_at_before_it_was_written":
                "The two bands were drawn as a translucent overlay on "
                "farm-out/ep2-b02-sapnat-0821/b02-sapnat-s20260820.png and "
                "opened at 1:1 before this spec existed. BROW [268,90,604,166] "
                "clears the top of the eyes by 11 px; MOUTH [334,274,506,350] "
                "starts 14 px below the nose and stops above the collar. The "
                "step rebuilds them from those same numbers rather than "
                "shipping a mask blob, so the geometry is auditable in the "
                "spec.",
            "plate_provenance":
                "farm-out/ep2-b02-sapnat-0821/b02-sapnat-s20260820.png, "
                "832x1216, sha256 30dce0fa.., asserted by the dry step and "
                "again by the repaint step before either loads a model. That "
                "is the plate round 2 of the canon-motion wave animated, so "
                "the only difference between round 2's clip and the next one "
                "is what this job paints.",
            "why_this_is_two_jobs_and_not_one":
                "It was one job first, and box_enqueue refused it twice. Its "
                "crop step's --src was a file three steps in the future, so "
                "the plate guard could not fetch the picture and the refs "
                "guard could not name the job that drew it -- two BLOCKS, "
                "both correct, both waivable with plate_ack: and neither "
                "worth waiving. Splitting costs one round trip and pays for "
                "itself twice: the guards get a real farm-out directory to "
                "read, and the plate is opened at 1:1 before eight GPU-"
                "minutes go on animating it.",
            "failure_predicted_in_advance":
                "THE REPAINT EATS THE FACE. 0.42 over a brow band 336 px wide "
                "is a large hole on a stylised anime face; the named "
                "degenerate outcome is a human brow ridge, a hairline, or a "
                "mouth with teeth in it -- all four are in the negative and "
                "F4 is what catches them. SECOND, CHEAPER: 0.42 is not enough "
                "to move a face that is drawn with this much ink and the "
                "brows come back as the same two flat strokes. F1 catches "
                "that, and the answer is a strength rung, not a new mask.",
        },
    },
    {
        "beat": 3,
        "parent": "pipeline/jobs/ep2-b03-canonmotion-r2-0821.yaml",
        "new_id": "ep2-b03-crouchlife-0822",
        "retoken": [],
        "seed": 20260843,
        "est": 9,
        "action": B03_ACTION,
        "prompt_key": "b03-motion-prompt.txt",
        "overrides": {},
        "fresh": {
            "owner": "the per-beat iteration lane, 2026-08-22",
            "consumer":
                "A CANDIDATE for beat 03 on review/ep2-beats-0821. The "
                "founder's note is about the shipped take's FACE; the fix for "
                "that face already exists in round 2's pixels and its only "
                "fault is that nothing happens in it. This job is that clip "
                "with an action. review/ep2-ship-0821 is not touched.",
            "success":
                "ONE 704x1280 105-frame 24fps mp4 that is NOT a still with a "
                "runtime. C1 his head is measurably lower at the midpoint "
                "than at f000 and back up by f096 -- the move has a start, a "
                "bottom and a return, and it is judged by eye on a frame "
                "strip; C2 the head turns off-centre at least once and comes "
                "back; C3 the identity round 2 won is kept -- no horn, no "
                "dissolve, features drawn in every frame, collar and ears "
                "intact; C4 the composited stem is still there, unmoved and "
                "un-multiplied; C5 the recede is no worse than round 2's 27% "
                "-- the fault this job is allowed to leave open, not one it "
                "may make worse.",
            "why":
                "HE IS OBJECTING TO A FACE THAT IS ALREADY FIXED IN A CLIP HE "
                "HAS NOT BEEN SHOWN. 'Wouldn't be that bad, if the goblin "
                "didn't look like an old man' is the shipped take, and the "
                "08-20 design audit says the same thing in its own words -- "
                "human nose with nostrils, a rounded human ear, folds either "
                "side of the mouth, flat olive skin. Round 2 of the canon-"
                "motion recipe drew his own tile's face instead and its "
                "verdict is unambiguous: R4 PASS, the horn from round 1 gone, "
                "features drawn in all 105 frames, collar and ears held, and "
                "R2 PASS on the trunk that beat 03 never used to have. Its "
                "one failure is R3: 'the pose barely changes from f000 to "
                "f104, there is no crouch and no sideways eye flick, and the "
                "only event in the clip is that his eyes CLOSE from about "
                "f096'. That job pre-registered A STILL WITH A RUNTIME by "
                "name and then hit it, and wrote down why -- it had asked a "
                "motion model to HOLD STILL.\n\nSo the design does not need "
                "another round. The action does. Same plate, same recipe, "
                "same identity clause byte-for-byte, and 'crouches low and "
                "holds still, eyes flicking sideways' replaced by three "
                "head-and-shoulder moves with a start, a bottom and a return. "
                "Eye flicks are dropped entirely: this engine was measured "
                "refusing gaze-only motion from both directions on beat 04 "
                "(rung 1 moved the whole head 64.7 px when told not to, rung "
                "2 locked the head to 4.7 px and the eyes stopped with it), "
                "and asking for them again would be re-running a closed "
                "experiment.",
        },
        "extra": {
            "the_one_variable":
                "THE ACTION WORDING. The init is round 2's plate unchanged, "
                "and so are 704x1280, 105 frames at 24fps, guidance, sampler, "
                "sigmas, two-stage, crf, offload, the cover-crop sha assert "
                "and the trim plan. The seed moves because an identical seed "
                "on an identical prompt returns the same file.",
            "what_the_body_can_actually_do_from_this_plate":
                "He is already squatting, front-on, knees apart, with the "
                "stem crossing his chest. Nothing in this action asks him to "
                "travel, stand, or reach past the stem -- it is head, neck "
                "and shoulders only, which is motion the plate has a body "
                "for. That distinction is what round 1 of the wave measured: "
                "the three beats that passed asked only for motion their "
                "plates could make, and the four that failed named something "
                "the picture did not contain.",
            "failure_predicted_in_advance":
                "THE DRIFT, NOT THE STILLNESS. Round 2 held its frame on beat "
                "02 -- whose action gives him somewhere to go -- and receded "
                "27% here, where the action was 'hold still'. Adding real "
                "body motion should help, and if C5 comes back WORSE than 27% "
                "that reading is falsified and the lever for this beat is "
                "frames or motion strength, not wording. SECOND: three "
                "sequential moves in 105 frames is a lot to ask; the cheap "
                "failure is the model doing the first one and holding, which "
                "C1 passes and C2 fails.",
        },
    },
]



# --------------------------------------------------------------------------
# BEAT 01, ROUND 2. Round 1 was opened at 1:1 against the take in the cut and
# it is WORSE, in two ways, and one of them is this lane's own fault.
#
#   THE COLOUR: round 1's fruit is TEAL. Not a taste call -- a mistake in the
#   rung. Rewriting the prompt to describe the silhouette dropped the words
#   "deep purple" out of it, so the only colour instruction the beat had went
#   with them. That is two variables in a rung that claimed one, it is
#   recorded here rather than quietly repaired, and it is why round 2 exists.
#   THE SHAPE: lumpy, with two stalk-like horns growing out of the top -- the
#   second failure round 1 predicted by name ("if the model reads 'sphere' and
#   'perfect circle' as a ban on roundness generally, the fruit can come back
#   lumpy"). A fig IS round; the thing to ban is the LOLLIPOP, not roundness.
#
# So round 2 restores the colour words verbatim, keeps a shorter silhouette
# clause, and bans only the ball-on-a-stick reading.
# --------------------------------------------------------------------------
B01_R2_PROMPT = (
    "On the thinnest branch of the tiny two-leaf sapling, the small green nub "
    "swells, darkens and ripens into a single deep purple fig -- teardrop "
    "shaped, heavy and rounded at the bottom, narrowing to a short thick neck "
    "where it meets the branch. It is the only thing in frame that moves. "
    "Detailed cinematic anime, warm amber backlight, hazy out-of-focus grassy "
    "field, soft glowing light, masterpiece, best quality, very aesthetic.")

B01_R2_NEGATIVE = (
    "lollipop, ball on a stick, bare thin stalk above the fruit, long stem, "
    "pin, antenna, two fruit, teal fruit, blue fruit, camera pan, camera "
    "tilt, zoom, dolly, push in, pull back, tripod, cut to another shot, "
    "scene change, different location, split screen, still image, freeze "
    "frame, growing plant, sprouting, unfurling leaves, stem lengthening, "
    "leaves enlarging, plant enlarging, blooming, brightening, exposure "
    "change, overexposed, blown highlights, changing background")

B01_R2_ROW = {
    "beat": 1,
    "parent": "pipeline/jobs/ep2-b01-figshape-0822.yaml",
    "new_id": "ep2-b01-figshape-r2-0822",
    "retoken": [("figshape-0822", "figshape-r2-0822")],
    "seed": 20260823,
    "est": 12,
    "overrides": {
        "payload:b01-motion-prompt.txt": B01_R2_PROMPT,
        "payload:b01-negative.txt": B01_R2_NEGATIVE,
    },
    "fresh": {
        "owner": "the per-beat iteration lane, 2026-08-22",
        "consumer":
            "A CANDIDATE for beat 01 on review/ep2-beats-0821, replacing a "
            "round 1 that is not offerable. review/ep2-ship-0821 is not "
            "touched.",
        "success":
            "ONE 704x1280 121-frame 24fps mp4. T1 THE FRUIT IS DEEP PURPLE at "
            "the end -- round 1 lost this and it is the beat's whole event; "
            "T2 the silhouette is a fig: wider across its bottom half than "
            "its top, with no bare stalk standing clear above it and NO horns "
            "or stalks growing out of the fruit itself, which is round 1's "
            "other fault; T3 the fruit is one clean body, not a blob with a "
            "second colour inside it; T4 the growth is continuous and is "
            "still the only thing moving.",
        "why":
            "ROUND 1 CAME BACK TEAL, AND THAT IS THIS LANE'S OWN MISTAKE "
            "RATHER THAN A FINDING. Rewriting the prompt to describe the "
            "silhouette dropped the words 'deep purple' out of it, so the "
            "beat's only colour instruction left with them and the fruit "
            "ripened to teal. The rung claimed one variable and moved two. "
            "Round 2 restores the colour words and keeps the silhouette "
            "clause, so the question round 1 was supposed to ask actually "
            "gets asked.\n\nTHE SHAPE ALSO FAILED, and that half WAS "
            "predicted: round 1's spec says in as many words that banning "
            "'sphere' and 'perfect circle' risks the model reading a ban on "
            "roundness generally and returning something lumpy. It did -- a "
            "flat blob with two stalk-like horns out of the top. A fig IS "
            "round; what the founder objected to is the LOLLIPOP reading, so "
            "round 2 bans that and nothing else about roundness.\n\nWHAT "
            "DID NOT CHANGE: the plate, 704x1280, 121 frames at 24fps, "
            "guidance, sampler, sigmas, two-stage, crf 33, offload.",
    },
    "extra": {
        "the_one_variable":
            "THE WORDING, again, and this time honestly one thing: the "
            "silhouette clause, with the colour instruction the beat has "
            "always had left in place. Round 1's negative is rewritten in the "
            "same pass because half of it was the cause of round 1's other "
            "fault -- leaving a ban that has been measured misfiring, in "
            "order to keep a tidy one-variable story, would be spending a "
            "render to re-confirm a known failure.",
        "next_rung_if_this_fails":
            "THE COMPOSITE. pipeline/nub_composite.py draws the frame-1 nub "
            "as an ellipse and the naturalise pass shades whatever it finds; "
            "a fig-shaped alpha there puts the silhouette in the pixels the "
            "way the fruit's COLOUR had to be put there in 2026-08-18 when "
            "the prompt route failed on colour. Two rounds of wording is the "
            "budget; this is round 2.",
        "failure_predicted_in_advance":
            "THE COLOUR COMES BACK AND THE SHAPE DOES NOT. 'Teardrop' is a "
            "weaker signal than 'deep purple' and the checkpoint's prior for "
            "a small fruit on a branch is a sphere. If T1 passes and T2 "
            "fails, wording is exhausted for this beat and the composite is "
            "the answer.",
    },
}


# --------------------------------------------------------------------------
# BEAT 02, STRENGTH RUNG. 0.42 was looked at at 1:1 and it did not do the job:
# the brows came back FAINTER rather than raised -- the pass washed the two
# existing strokes out instead of drawing new ones -- and the mouth opened
# only slightly. That is the failure this spec's own
# `failure_predicted_in_advance` named before the pixels ("0.42 is not enough
# to move a face drawn with this much ink ... the answer is a strength rung,
# not a new mask"), so the mask is untouched and only the number moves.
# TWO strengths in one job, which is the same trade ep2-jerry-expref-r2-0821
# made on this exact question: the band is 0.55-0.80, the cost of bracketing
# it is four minutes, and one sample per rung would spend two round trips
# finding out what one job can say.
# --------------------------------------------------------------------------
def b02_strength_steps(child: dict) -> None:
    root = r"C:\banyan-farm\b02panicstr-0822"
    mask = root + r"\b02-panic-mask.png"

    def face(tag, strength):
        return {"name": "face" + tag, "argv": [
            BOXPY, root + r"\inpaint_fruit.py",
            "--init", B02_PLATE, "--init-sha256", B02_PLATE_SHA,
            "--mask-png", mask,
            "--prompt-file", root + r"\b02-face-prompt.txt",
            "--negative-file", root + r"\b02-face-negative.txt",
            "--out", root + ("\\b02-panic-s%s.png" % tag),
            "--steps", "40", "--cfg", "7.5", "--strength", strength,
            "--pad-crop", "64", "--blur", "8", "--seed", "20260822",
            "--note", "STRENGTH RUNG. Same plate, same two bands, same seed, "
                      "same everything as the 0.42 pass that came back with "
                      "washed-out brows. Only the denoise moves."]}

    publish_code = (
        "import hashlib, os, shutil\n"
        "from_dir = 'C:/banyan-farm/b02panicstr-0822'\n"
        "dst = 'C:/banyan-farm/courier-box/farm-out/ep2-b02-panicstr-0822'\n"
        "NAMES = ['b02-panic-s060.png', 'b02-panic-s060.png.meta.yaml',\n"
        "         'b02-panic-s075.png', 'b02-panic-s075.png.meta.yaml',\n"
        "         'b02-panic-mask.png', 'b02-face-prompt.txt',\n"
        "         'b02-face-negative.txt']\n"
        "os.makedirs(dst, exist_ok=True)\n"
        "lines = []\n"
        "for name in NAMES:\n"
        "    f = os.path.join(from_dir, name)\n"
        "    if not os.path.isfile(f):\n"
        "        raise SystemExit('!! missing %s -- refusing to call the job "
        "clean.' % f)\n"
        "    shutil.copy2(f, dst)\n"
        "    with open(os.path.join(dst, name), 'rb') as fh:\n"
        "        lines.append(hashlib.sha256(fh.read()).hexdigest() + '  ' + name)\n"
        "with open(os.path.join(dst, 'ep2-b02-panicstr-0822.sha256'), 'w',\n"
        "          newline='\\n') as fh:\n"
        "    fh.write('\\n'.join(sorted(lines)) + '\\n')\n"
        "print('published', len(lines), 'file(s) + manifest ->', dst)\n"
        "raise SystemExit(0 if len(lines) == len(NAMES) else 1)\n")

    steps = [s for s in child["steps"] if s.get("name") in ("mask", "dry")]
    if len(steps) != 2:
        raise SystemExit("!! beat 02 strength rung: the parent lost its mask "
                         "or dry step")
    child["steps"] = steps + [face("060", "0.60"), face("075", "0.75"),
                              {"name": "publish", "argv": [BOXPY, "-c",
                                                           publish_code]}]
    child["artifacts"] = [root + r"\b02-panic-s060.png",
                          root + r"\b02-panic-s075.png"]


B02_STRENGTH_ROW = {
    "beat": 2,
    "parent": "pipeline/jobs/ep2-b02-panicface-0822.yaml",
    "new_id": "ep2-b02-panicstr-0822",
    "retoken": [("b02panicface-0822", "b02panicstr-0822")],
    "seed": 20260822,
    "est": 6,
    "post": b02_strength_steps,
    "overrides": {},
    "fresh": {
        "owner": "the per-beat iteration lane, 2026-08-22",
        "consumer":
            "THE PLATE beat 02's motion round runs on, second attempt. Two "
            "strengths so the band is bracketed in one job rather than two "
            "round trips. Nothing downstream is filed until one of them is "
            "looked at at 1:1.",
        "success":
            "TWO 832x1216 pngs, and at least one of them has BROWS THAT READ "
            "AS RAISED -- angled up and away from the eyes, drawn, not washed "
            "out -- and a mouth open wider than the small oval the source "
            "plate has. G1 brows raised and drawn; G2 mouth open wide; G3 the "
            "eyes are byte-identical to the source plate, because they are "
            "outside the mask; G4 nothing outside the two bands moved; G5 no "
            "human brow ridge, no hairline, no teeth. If BOTH overshoot G5, "
            "the answer is a smaller mask, not a third strength.",
        "why":
            "0.42 WAS LOOKED AT AND IT WASHED THE BROWS OUT INSTEAD OF "
            "RAISING THEM. Opened at 1:1 against its own source: the two brow "
            "strokes came back FAINTER and slightly angled, the mouth opened "
            "a little, and the result reads no more panicked than the plate "
            "it started from -- which is the founder's whole note on this "
            "beat. Everything else the plate job asked for passed: the eyes "
            "are untouched because they are outside the mask, nothing outside "
            "the two bands moved, and no human brow ridge or hairline "
            "appeared.\n\nThat outcome was written down before the pixels: "
            "the plate job's own failure_predicted_in_advance says '0.42 is "
            "not enough to move a face that is drawn with this much ink and "
            "the brows come back as the same two flat strokes ... the answer "
            "is a strength rung, not a new mask'. So the mask does not move, "
            "the prompt does not move, the seed does not move, and the "
            "denoise goes to 0.60 and 0.75.",
    },
    "extra": {
        "the_one_variable":
            "THE DENOISE, at two values. Same source plate, same two bands to "
            "the pixel, same prompt, same negative, same 40 steps, same cfg "
            "7.5, same pad-crop 64 and blur 8, same seed 20260822. Two "
            "strengths is a bracket, not a second question -- the range worth "
            "trying is 0.55-0.80 and finding out costs four minutes.",
        "failure_predicted_in_advance":
            "0.75 REDRAWS THE FACE RATHER THAN ITS EXPRESSION. At that "
            "denoise the pass is running most of its steps from noise inside "
            "the mask, and the named degenerate outcome is a human brow "
            "ridge, a hairline creeping down the forehead, or a mouth with "
            "teeth and a tongue in it -- all in the negative, and G5 is what "
            "catches them. If 0.75 overshoots and 0.60 undershoots, the "
            "reading is that this face's ink is stronger than the band and "
            "the next lever is a tighter mask around the brows alone.",
    },
}


# --------------------------------------------------------------------------
# THE SECOND HALF OF BEAT 02, filed only once the repainted plate is on disk
# and has been looked at. It is a row like any other; it just cannot be
# written before its input exists, because its input's digest is half of it.
# --------------------------------------------------------------------------
B02_MOTION_PLATE_REL = "farm-out/ep2-b02-panicstr-0822/b02-panic-s060.png"
B02_MOTION_PLATE_BOX = (r"C:\banyan-farm\courier-box\farm-out"
                        r"\ep2-b02-panicstr-0822\b02-panic-s060.png")


def b02_motion_row(plate_sha: str) -> dict:
    return {
        "beat": 2,
        "parent": "pipeline/jobs/ep2-b02-canonmotion-r2-0821.yaml",
        "new_id": "ep2-b02-panic-0822",
        "retoken": [],
        "seed": 20260842,
        "est": 9,
        "action": B02_ACTION,
        "negative_extra": B02_NEGATIVE_EXTRA,
        "prompt_key": "b02-motion-prompt.txt",
        "negative_key": "b02-negative.txt",
        "overrides": {
            "argv:--src": B02_MOTION_PLATE_BOX,
            "argv:--sha256": plate_sha,
        },
        "fresh": {
            "owner": "the per-beat iteration lane, 2026-08-22",
            "consumer":
                "A CANDIDATE for beat 02 on review/ep2-beats-0821, answering "
                "both halves of the founder's 2026-08-21 note -- the face "
                "through the plate under it, the landing through this job's "
                "action wording. review/ep2-ship-0821 is not touched; the "
                "clip is a candidate until he rules.",
            "success":
                "ONE 704x1280 105-frame 24fps mp4. P1 THE FACE IS NOT "
                "SOLDIERLY: the brows stay up and the mouth stays open "
                "through the trim, judged at 1:1 against the shipped take's "
                "flat mouth line -- the half his note leads with. P2 HE DOES "
                "NOT FACEPLANT: at f096, the last frame the 97-frame trim "
                "keeps, he is prone on his chest with his chin clear of the "
                "ground and his head up. P3 the entry-skid-dive still reads "
                "as three phases and completes by f096. P4 the frame does "
                "not pull back and the composited sapling is still there, "
                "unmoved and un-multiplied -- round 2 won both and losing "
                "them is a regression however good the face is. P5 ears, "
                "skin colour, slit pupils and clothes are the plate's.",
            "why":
                "THE PLATE UNDER THIS CLIP ALREADY CARRIES THE PANIC, so this "
                "job only has to not lose it and to fix the landing.\n\nTHE "
                "FACE was moved by ep2-b02-panicface-0822, a masked i2i over "
                "the brow and mouth bands of round 2's own init -- the route "
                "ep2-jerry-expref-r2-0821 measured working after four "
                "prompt-side interventions measured failing. The motion "
                "prompt's existing 'his face DOES NOT CHANGE' clause is "
                "carried byte-for-byte and is now working FOR the note "
                "instead of against it: round 2 proved that clause holds a "
                "face for all 105 frames, and the face it will hold is the "
                "panicked one.\n\nTHE LANDING. 'He just faceplants into the "
                "ground.' Round 2's own verdict says the same thing from the "
                "other side -- the plate fixed the camera and left 'the SHAPE "
                "of the move' wrong: 'there is no entry, no skid, and the "
                "dive reads as a duck'. The script says he 'sprints into "
                "frame, skids, and dives behind the sapling's thin trunk', "
                "and the end state that implies is behind cover, not nose-"
                "first in the dirt. So the landing is written as a PLACEMENT "
                "-- forearms take it, chin off the ground, prone with the "
                "head up -- which is the wording form this engine has been "
                "measured following, rather than an adjective it has been "
                "measured ignoring.\n\nWHAT DID NOT CHANGE: 704x1280, 105 "
                "frames at 24fps, guidance, sampler, sigmas, two-stage, crf, "
                "offload, the cover-crop sha assert and the trim-to-97 plan.",
        },
        "extra": {
            "the_one_variable":
                "TWO, AND THEY ARE SCORED SEPARATELY SO THE RESULT STAYS "
                "READABLE: the init plate now carries a panicked face, and "
                "THE ACTION now names the landing as a placement. P1 reads "
                "the first, P2 and P3 the second. They are run together "
                "because they answer one note and neither can be judged from "
                "a still.",
            "plate_provenance":
                "%s, sha256 %s.., produced by ep2-b02-panicstr-0822 from "
                "farm-out/ep2-b02-sapnat-0821/b02-sapnat-s20260820.png by a "
                "0.60 masked i2i over two face bands (brow and mouth; the "
                "eyes are outside the mask and are byte-identical to the "
                "source). THE STRENGTH WAS PICKED BY EYE FROM A BRACKET, not "
                "assumed: 0.42 washed the brows out, 0.60 draws them raised "
                "and arched with the mouth open, and 0.75 overshot into a "
                "scowl with sweat drops and a jagged mouth eating the collar. "
                "cover_crop.py asserts the digest above before it writes an "
                "init frame."
                % (B02_MOTION_PLATE_REL, plate_sha[:8]),
            "failure_predicted_in_advance":
                "THE MODEL TAKES THE EASY HALF OF A COMPOUND ACTION, which is "
                "exactly how round 2 failed here -- it kept the frame and "
                "dropped the skid. If this returns the prone landing without "
                "the entry and skid, P2 passes and P3 fails, and the next "
                "rung is a SHORTER action, not a stronger one. SECOND: LTX "
                "relaxes a repainted face back toward the checkpoint's own "
                "default over 105 frames, so the panic fades late in the "
                "clip; P1 is judged across the trim and not on frame 0.",
        },
    }


def build(row: dict) -> dict:
    parent = row["parent"]
    pspec = _yaml.safe_load(open(os.path.join(REPO, parent), encoding="utf-8"))
    overrides = dict(row["overrides"])

    if "action" in row:
        pkey = [k for k in pspec["payload"] if row["prompt_key"] in k][0]
        prompt = head_of(pspec["payload"][pkey]) + " " + row["action"]
        overrides["payload:" + row["prompt_key"]] = prompt
    if row.get("negative_extra"):
        nkey = [k for k in pspec["payload"] if row["negative_key"] in k][0]
        overrides["payload:" + row["negative_key"]] = (
            pspec["payload"][nkey].rstrip() + row["negative_extra"])

    overrides["seed"] = row["seed"]
    overrides["key:priority"] = 14
    overrides["key:est_minutes"] = row["est"]

    child = derive_spec.derive(
        parent, row["new_id"],
        fresh=row["fresh"], overrides=overrides, extra=row["extra"],
        retoken=row.get("retoken") or None,
        by="pipeline/file_beatfix_0822.py",
    )
    if row.get("post"):
        row["post"](child)
    return child


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--b01-r2", action="store_true",
                    help="file beat 01's round 2 after round 1 has been "
                         "looked at.")
    ap.add_argument("--b02-strength", action="store_true",
                    help="file beat 02's strength rung on the repainted "
                         "plate, after the 0.42 pass has been looked at.")
    ap.add_argument("--b02-motion", action="store_true",
                    help="file beat 02's MOTION job instead of the three "
                         "first-round jobs. Refuses until the repainted plate "
                         "is on disk, because its digest is half the spec.")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    if a.b01_r2:
        child = build(B01_R2_ROW)
        print("%-26s beat 01  %d step(s)  est %d min"
              % (B01_R2_ROW["new_id"], len(child["steps"]), B01_R2_ROW["est"]))
        if a.write:
            path = derive_spec.write(
                child, "pipeline/jobs/%s.yaml" % B01_R2_ROW["new_id"],
                force=a.force)
            print("   wrote %s" % os.path.relpath(path, REPO))
        else:
            print("\n-- dry run. re-run with --write.")
        return 0

    if a.b02_strength:
        child = build(B02_STRENGTH_ROW)
        print("%-26s beat 02  %d step(s)  est %d min"
              % (B02_STRENGTH_ROW["new_id"], len(child["steps"]),
                 B02_STRENGTH_ROW["est"]))
        if a.write:
            path = derive_spec.write(
                child, "pipeline/jobs/%s.yaml" % B02_STRENGTH_ROW["new_id"],
                force=a.force)
            print("   wrote %s" % os.path.relpath(path, REPO))
        else:
            print("\n-- dry run. re-run with --write.")
        return 0

    if a.b02_motion:
        if not os.path.isfile(os.path.join(REPO, B02_MOTION_PLATE_REL)):
            raise SystemExit(
                "!! %s is not here yet. ep2-b02-panicface-0822 has to land "
                "and be LOOKED AT before this job is worth filing -- that is "
                "the whole reason beat 02 is two jobs." % B02_MOTION_PLATE_REL)
        row = b02_motion_row(sha_of(B02_MOTION_PLATE_REL))
        child = build(row)
        print("%-26s beat 02  seed %d  %d step(s)  est %d min  plate %s.."
              % (row["new_id"], row["seed"], len(child["steps"]), row["est"],
                 sha_of(B02_MOTION_PLATE_REL)[:12]))
        if a.write:
            path = derive_spec.write(child, "pipeline/jobs/%s.yaml"
                                     % row["new_id"], force=a.force)
            print("   wrote %s" % os.path.relpath(path, REPO))
        else:
            print("\n-- dry run. re-run with --write.")
        return 0

    # The SDXL prompts are the only ones CLIP has to swallow. The LTX motion
    # prompts go through T5 and are long by design -- counting them against 77
    # would be counting the wrong tokeniser.
    assert_under_clip77("b02 face prompt", B02_FACE_PROMPT)
    assert_under_clip77("b02 face negative", B02_FACE_NEGATIVE)

    have = sha_of(B02_PLATE_REL)
    if have != B02_PLATE_SHA:
        raise SystemExit("!! %s hashes %s, this filer names %s"
                         % (B02_PLATE_REL, have, B02_PLATE_SHA))

    for row in ROWS:
        child = build(row)
        blob = _yaml.safe_dump({k: v for k, v in child.items()
                                if k != "derivation"})
        if row["beat"] == 2 and B02_PLATE_SHA not in blob:
            raise SystemExit("!! beat 02: the plate digest did not reach the "
                             "child spec")
        out = "pipeline/jobs/%s.yaml" % row["new_id"]
        print("%-26s beat %02d  seed %d  %d step(s)  est %d min"
              % (row["new_id"], row["beat"], row["seed"],
                 len(child["steps"]), row["est"]))
        if a.write:
            path = derive_spec.write(child, out, force=a.force)
            print("   wrote %s" % os.path.relpath(path, REPO))

    if not a.write:
        print("\n3/3 derived, clip77 counted, plate re-hashed. "
              "-- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
