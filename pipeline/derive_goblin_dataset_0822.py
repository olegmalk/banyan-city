#!/usr/bin/env python3
r"""THE GOBLIN DATASET FACTORY: 32 CELLS OF HIS OWN FACE, RE-LIT AND RE-GROUNDED.

WHAT THIS IS AND WHY IT IS NOT ANOTHER ROUND OF FACE WORK.
`pipeline/goblin-i2i-route-0822.md` closed the img2img route as a POSING route
on a mechanism -- at strength <= 0.40 only the last s*N steps run, global
structure is decided in the high-noise steps that never execute, so the pose
cannot move and the face survives FOR THE SAME REASON. Section 3 of that doc
kept the other half:

  > img2img-from-canon at <= 0.40 DOES make new pictures of him with his face
  > intact -- different light, different grass, different background, at 5
  > seconds a frame for $0. It is a re-lighting and re-grounding route.

Section 4 named the only remaining path to a POSEABLE goblin: a LoRA trained on
his pixels, because a LoRA and a skeleton can both act at strength 1.0 where
there is no init competing with them. And it named where the training frames
come from -- this route, run as a factory. That is this file. Every frame it
makes is the founder's own drawing, re-lit; nothing here invents a face, which
is the thing `route_closure_2026_08_22` forbids and sixteen rounds proved
impossible.

THE THREE AXES, AND WHY EACH ONE IS THE AXIS IT IS.

  1. THE INIT (6 values). Framing and handedness CANNOT come from the prompt on
     this route -- that is round two's finding, not a guess: composition is
     decided in steps the pass never runs, so `upper body` and `from the left`
     are dead letters at 0.35. They come from `build_jerry_inits_0822.py`, which
     cuts the canon into full / cowboy / square-head and mirrors each. This is
     the axis the sapling v1 verdict says matters most: 44 of 44 frames at ONE
     distance on ONE ground taught the trigger the field, and
     `curation-tile-0820` refused a goblin dataset outright for the same reason
     -- "seven frames in four poses trains a pose, not a character".

  2. THE GROUND (12 values). Straight out of the sapling lane's measured
     vocabulary (`derive_saplora_figplate_0822`), INCLUDING its correction: the
     material must be the SUBJECT of the clause and not an adjective inside a
     location clause. That lane asked for `in a ploughed field of bare brown
     earth` and got a planted vegetable bed -- the earth arrived and `bare` did
     not. Every clause below leads with the surface he stands ON.

  3. THE LIGHT (11 values). The axis this route is measurably BEST at: round
     one's s40 moved light and palette with E1-E5 intact, and round two's
     control measured the no-net twin departing from the init by 7.13 mean abs
     at 0.30 -- real change, face held.

WHAT IS DELIBERATELY *NOT* AN AXIS, AND THIS IS A SAVED HOUR RATHER THAN AN
OVERSIGHT: CAMERA ANGLE VIA WORDS. The brief asked for `subtle camera angles via
words`, and the route doc already closed it. `from below` and `high angle` are
instructions about GLOBAL STRUCTURE, decided in the high-noise steps this pass
never enters -- the same mechanism that made a full-strength OpenPose skeleton
at scale 1.0 fail to bend a single knee. Spending four cells to re-measure a
closed mechanism is the thing this lane keeps catching itself doing. The angle
variety in the set is REAL and comes from the crops instead: the head square is
a closer camera and the cowboy is a mid, and both are geometry rather than
persuasion.

THE STRENGTH IS NOT AN AXIS EITHER, IT IS A BUDGET. 0.40 is the measured
ceiling (round one: the face breaks between 0.40 and 0.45) and it buys the most
scene change, so most cells sit there. 0.35 and 0.30 cells exist so the set is
not a monoculture of one denoising depth -- a set drawn entirely at one strength
carries that strength's rendering signature in every frame.

THE CAPTIONS ARE SHORT, AND THE RULE IS MEASURED RATHER THAN STYLISTIC.
`registry.yaml`'s v2b entry is the finding: v2 lengthened every caption by two
clauses and identity went 11/15 -> 9/15; v2b gave the original captions back,
changed nothing else, and identity came back to 11/15 EXACTLY. The rule it
states is now binding on this tree -- "do not lengthen the captions of frames
that are already working in order to describe frames that are new. Name a new
axis on the frames that carry it." Every caption here is the SAME ten clauses
with THREE slots filled differently, so no frame in the set carries a longer
caption than any other and the trigger's share of every caption is identical.

AND THE THREE CONSTANT CLAUSES ARE THE POINT OF THE WHOLE EXERCISE. Every
caption says `standing`, `looking at viewer` and a framing word even though the
first two never vary -- because a named attribute is one the token is EXCUSED
from carrying, and the one thing this LoRA must not learn is a pose. The entire
reason it is being trained is that a pose net has to be able to move him. A set
cut from one standing picture, captioned without the word `standing`, would fuse
standing into `bnyjerry` and reproduce the pose lock at the training level that
img2img has at the sampling level. That would be the same failure one layer
down, and it is prevented by three words.

NO FACE TERM APPEARS ANYWHERE, IN PROMPT, NEGATIVE OR CAPTION.
`assert_no_face_terms` is imported from round one rather than re-typed and is run
over the CAPTIONS too, which round one had no captions to check. His face is the
init's pixels and the LoRA's job; a word describing it is both the closed route
and the caption rule's `a named attribute is one the token is excused from
carrying`, failing in the same direction.

ONE SAMPLE BEFORE ANY BATCH (founder, 2026-08-03), AND THERE ARE EXACTLY THREE
RECIPE CHANGES, SO THERE ARE THREE SAMPLE CELLS -- one each, not one per cell
and not one for the lot:
    j01  a NON-GRASS GROUND CLAUSE on this route. No goblin i2i frame has ever
         asked for anything but the init's own meadow.
    j14  a CROPPED AND MIRRORED INIT. The pipeline has never been handed
         anything but the canon at 832x1216.
    j21  AN 832x832 FRAME. A new mask size, a new aspect, and the first square
         this driver has ever run.
`--batch` REFUSES until all three are rendered and judged, exactly the gate
`derive_saplora_figplate_0822` puts in front of its own batch.

  python3 pipeline/derive_goblin_dataset_0822.py               # dry, all 32
  python3 pipeline/derive_goblin_dataset_0822.py --sample --write
  python3 pipeline/derive_goblin_dataset_0822.py --batch --write
  python3 pipeline/derive_goblin_dataset_0822.py --cell j07 --write
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard                                       # noqa: E402
import derive_spec                                              # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77       # noqa: E402
from derive_goblin_i2i_0822 import assert_no_face_terms         # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = "pipeline/jobs/ep2-b13-i2icanon-s30-0822.yaml"
PARENT_DIRTOK = "b13i2icanon-s30-0822"
PARENT_OUTTOK = "b13-i2icanon-s30"
PARENT_INITTOK = "goblin-canon-founder-0821"
PARENT_MASKTOK = "fullframe-mask-0822"
PARENT_SEEDTOK = "s20260820"

SRC_DIR = "farm-out/ep2-goblin-i2i-src-0822"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
SEED0 = 20260901          # + the cell's index, so every cell is its own draw
SAMPLE_CELLS = ("j01", "j14", "j21")

# ── THE STRENGTH SWEEP, ADDED AFTER THE SAMPLE GATE CAUGHT WHAT IT IS FOR.
#
# The three sample cells came back and TWO of them failed the E-bar, in one
# direction, with one cause:
#
#     j01  full body   (face ~15% of the frame) at 0.40 -- E2/E3/E4/E5 hold,
#          the almond eye holds, and THE PUPIL WENT YELLOW.
#     j14  cowboy shot (face ~29%)              at 0.40 -- pupils PINK, ears
#          bigger and swept UP. Drifting toward the vetoed design.
#     j21  square head (face ~49%)              at 0.40 -- eyes LARGER and
#          ROUNDER with red pupils, ears larger and upswept. The worst of the
#          three, on the tightest crop.
#
# THE FINDING, AND IT IS THE SAME MECHANISM THE WHOLE ROUTE RUNS ON, ARRIVING ON
# A NEW AXIS: strength is a UNIFORM denoising depth over the frame, but a face
# that occupies half the frame has three times the latent area of a face that
# occupies a sixth. At a fixed strength the big face gives animagine's prior
# three times as much room to re-resolve, and it does -- into exactly the round
# coloured iris and the tall upswept ear that `route_closure_2026_08_22`
# describes as the vetoed design and that sixteen prompt-side rounds produced.
# LESS OF HIS FACE REACHING THE DENOISER PRODUCED MORE OF HIS FACE, which is
# round nine's sentence about the ENCODER holding for PIXELS too.
#
# SO THE STRENGTH IS NOT ONE NUMBER, IT IS ONE NUMBER PER FRAMING, and the batch
# does not run until each framing's number is measured. This is one variable per
# cell: the framing is fixed within a row, the ground and light are held to what
# the sample cell used, and only the strength moves.
SWEEP_CELLS = ("k01", "k02", "k03", "k04", "k05", "k06", "k07", "k08")

# ── ROUND TWO OF THE SWEEP, AND IT EXISTS BECAUSE ROUND ONE ANSWERED TWO OF ITS
# THREE ROWS AND KILLED THE THIRD.
#
#   COWBOY  ANSWERED. 0.20 holds his face exactly -- narrow almond, TINY DARK
#           pupil, ears near horizontal, and the background genuinely moved.
#           0.25 opens the eye toward round and lifts the ears. The number is
#           0.20 and it is measured, not chosen.
#   FULL    NOT ANSWERED. The eye SHAPE holds at 0.40 and at 0.30, and the PUPIL
#           GOES YELLOW at both. A tiny yellow pupil is a smaller miss than the
#           round iris sixteen rounds produced, and it is still a colour that is
#           not his, on the one axis that has four founder vetoes on it. In a
#           TRAINING SET a consistent wrong pupil colour is worse than in a
#           plate, because the trigger would learn it. So the row continues
#           downward until the pupil comes back dark.
#   HEADSQ  DEAD. Drifted at 0.40, 0.20 and 0.15 -- its own floor. Replaced by
#           `headnat`, which magnifies nothing. 0.25 and 0.30 on that row were
#           NOT judged and are not claimed to have been: a row whose floor fails
#           cannot be rescued by its ceiling, and rendering two more frames to
#           watch a monotonic curve get worse is the spend this lane is supposed
#           to refuse.
M_CELLS = ("m01", "m02", "m03", "m04", "m05")

# init key -> (file, size, framing caption word)
#
# THE FRAMING WORD IS A CAPTION TOKEN AND IT IS NOT DECORATION. It is the third
# of the three clauses that excuse the trigger from carrying something it must
# not carry: `standing` and `looking at viewer` free the pose and the gaze, and
# this frees the DISTANCE. Danbooru vocabulary, because animagine-xl-3.1's text
# encoder was trained on it.
INITS = {
    "full":        ("init-full-0822.png",        (832, 1216), "full body"),
    "full-flip":   ("init-full-flip-0822.png",   (832, 1216), "full body"),
    "cowboy":      ("init-cowboy-0822.png",      (832, 1216), "cowboy shot"),
    "cowboy-flip": ("init-cowboy-flip-0822.png", (832, 1216), "cowboy shot"),
    "headsq":      ("init-headsq-0822.png",      (832, 832),  "portrait"),
    "headsq-flip": ("init-headsq-flip-0822.png", (832, 832),  "portrait"),
    # THE NATIVE SQUARE, headsq's replacement. 1.000x -- see
    # build_jerry_inits_0822.py, which explains why the magnified one is dead.
    # `upper body` rather than `portrait`: this frame holds head, torso AND
    # hands, and a caption has to describe the frame that arrived.
    "headnat":      ("init-headnat-0822.png",      (832, 832), "upper body"),
    "headnat-flip": ("init-headnat-flip-0822.png", (832, 832), "upper body"),
}

# cell -> (init, strength, ground clause for the PROMPT, ground word for the
#          CAPTION, light clause for the PROMPT, light word for the CAPTION)
#
# THE PROMPT CLAUSE AND THE CAPTION WORD ARE KEPT ON ONE LINE SO THEY CANNOT
# DRIFT APART. The prompt is what the card is asked for; the caption is what the
# trainer is told arrived. If a cell is admitted, the caption must describe the
# frame that came back -- so a cell whose ground did NOT arrive is dropped at
# judging rather than re-captioned around, which is how a dataset acquires a lie.
#
# THE HEAD CELLS NAME A BACKDROP, NOT A ROOTING SURFACE. At a portrait crop the
# ground is three per cent of the frame and out of focus; asking for gravel there
# would put a word in the caption that the pixels do not carry.
CELLS = {
    # ══════════════════════════════════════════════════════════════════════
    # THE BATCH, REBUILT ON THE MEASURED WINDOW. The `n` cells are the dataset;
    # the `j`, `k` and `m` cells below them are the sample and the two sweep
    # rounds that produced the numbers these use, kept because they are the
    # evidence and because four of them are admitted frames in their own right.
    #
    # WHAT THE SWEEP MEASURED, IN ONE TABLE. Face fraction is the share of the
    # frame his head occupies; mag is the init's magnification off the canon.
    #
    #   init      face   mag     result
    #   full      15%   1.000x   eye SHAPE holds at every strength, PUPIL YELLOW
    #                            at 0.40/0.35/0.30/0.25/0.20. Five points.
    #   headnat   22%   1.000x   HOLDS at 0.30 and 0.25 and 0.20.
    #   cowboy    29%   1.387x   HOLDS at 0.20. Eye opens at 0.25.
    #   headsq    49%   1.486x   drifts at 0.40, 0.20 and 0.15. Retired.
    #
    # THE FINDING, AND IT IS TWO-SIDED. His eye survives only inside a WINDOW of
    # face fraction. Above it -- j14 at 29% and 0.25, j21 at 49% -- animagine's
    # prior has enough latent area to re-resolve the face and returns the round
    # coloured iris and the tall upswept ear that four founder vetoes name. BELOW
    # it -- every full-body cell -- his eye is a handful of latent cells, a tiny
    # dark pupil in a narrow almond cannot be carried at that resolution, and the
    # prior repaints the iris warm no matter how few steps run. The route doc's
    # law reads a third time: HIS PIXELS HAVE TO ENTER AS PIXELS, at a size the
    # latent grid can hold, and not as an interpolation of them.
    #
    # SO THE DATASET IS TWO RENDERED FRAMINGS AND ONE THAT IS NOT RENDERED AT ALL:
    #   headnat / headnat-flip  at 0.25 and 0.30  -- the workhorse, 12 cells
    #   cowboy  / cowboy-flip   at 0.20           -- the wider view,  8 cells
    #   full    / full-flip     AT ZERO STRENGTH  -- the canon image itself and
    #       its mirror, entered as training frames directly. They cannot drift
    #       because nothing was denoised; they cost no GPU second; and they are
    #       the only way this set sees his boots, his legs and his whole
    #       silhouette, which a bust-only dataset would never teach.
    #
    # AND THE SECOND SLOT OF EVERY CAPTION IS NOW A SETTING, NOT A GROUND
    # MATERIAL. j01 measured that the surface underfoot does NOT change on this
    # route -- it is global structure, decided in steps a low strength never runs,
    # which is the same sentence as everything else here. What DOES change is the
    # far background and the light, measured on every admitted frame. Captioning
    # a ground that did not arrive would be the lie build_jerry_v2_0822.py has no
    # code path to write, so the axis is named as what it is.
    # ══════════════════════════════════════════════════════════════════════

    "n01": ("headnat", "0.30", "standing against a pale open sky",
           "a pale sky", "low golden sun", "warm low sunlight"),
    "n02": ("headnat-flip", "0.30", "standing against a dark forest",
           "a dark forest", "dappled shade under leaves", "dappled shade"),
    "n03": ("headnat", "0.25", "standing against a grey stone wall",
           "a stone wall", "flat overcast light", "overcast light"),
    "n04": ("headnat-flip", "0.25", "standing against an open field",
           "an open field", "cool morning haze", "cool morning light"),
    "n05": ("headnat", "0.30", "standing against a warm sunset sky",
           "a sunset sky", "warm rim light", "rim light"),
    "n06": ("headnat-flip", "0.30", "standing against a wet grey sky after rain",
           "a rainy sky", "grey light after rain", "grey wet light"),
    "n07": ("headnat", "0.25", "standing against a green hedgerow",
           "a hedgerow", "strong side light", "hard side light"),
    "n08": ("headnat-flip", "0.25", "standing against a wall of ferns",
           "a wall of ferns", "deep shade", "deep shade"),
    "n09": ("headnat", "0.30", "standing against distant blue hills",
           "distant hills", "bright midday sun", "bright sunlight"),
    "n10": ("headnat-flip", "0.30", "standing against a weathered barn wall",
           "a barn wall", "warm lamplight", "warm lamplight"),
    "n11": ("headnat", "0.25", "standing against a ploughed brown field",
           "a ploughed field", "long evening light", "warm evening light"),
    "n12": ("headnat-flip", "0.25", "standing against a pale sand horizon",
           "a sand horizon", "heavy overcast, soft shadowless light", "shadowless light"),
    "n13": ("cowboy", "0.20", "standing against a pale open sky",
           "a pale sky", "low golden sun", "warm low sunlight"),
    "n14": ("cowboy-flip", "0.20", "standing against a dark forest",
           "a dark forest", "dappled shade under leaves", "dappled shade"),
    "n15": ("cowboy", "0.20", "standing against a grey stone wall",
           "a stone wall", "flat overcast light", "overcast light"),
    "n16": ("cowboy-flip", "0.20", "standing against an open field",
           "an open field", "cool morning haze", "cool morning light"),
    "n17": ("cowboy", "0.20", "standing against a warm sunset sky",
           "a sunset sky", "warm rim light", "rim light"),
    "n18": ("cowboy-flip", "0.20", "standing against distant blue hills",
           "distant hills", "bright midday sun", "bright sunlight"),
    "n19": ("cowboy", "0.20", "standing against a green hedgerow",
           "a hedgerow", "strong side light", "hard side light"),
    "n20": ("cowboy-flip", "0.20", "standing against a wet grey sky after rain",
           "a rainy sky", "grey light after rain", "grey wet light"),

    # ── BACKFILL. Seven of the nineteen were dropped and one (n18) never
    # rendered, which left the set at 18 against a target of 20. Five of the
    # seven drops failed on PUPIL COLOUR ALONE -- everything else about those
    # faces is his -- and pupil colour is a per-seed lottery on this route, not a
    # property of the cell. So the three cleanest of those cells are re-drawn at
    # a NEW SEED, nothing else moved, and n18 is finally fired. A reseed is not a
    # second chance at a judgement; the new frame is judged from scratch and the
    # old one stays dropped either way.
    "p03": ("headnat", "0.25", "standing against a grey stone wall", "a stone wall",
            "flat overcast light", "overcast light"),
    "p07": ("headnat", "0.25", "standing against a green hedgerow", "a hedgerow",
            "strong side light", "hard side light"),
    "p17": ("cowboy", "0.20", "standing against a warm sunset sky", "a sunset sky",
            "warm rim light", "rim light"),
    "p18": ("cowboy-flip", "0.20", "standing against distant blue hills", "distant hills",
            "bright midday sun", "bright sunlight"),

    # ── THE THREE SAMPLE CELLS. All three were DROPPED and all three are kept
    # here, because their paths, seeds and captions have to resolve for the
    # admissions record to name them -- and because they are the measurements
    # the whole batch above is built on.
    "j01": ("full", "0.40", "standing on dry cracked bare earth, a green hedgerow far behind",
            "dry cracked earth", "low golden sun", "warm low sunlight"),
    "j14": ("cowboy-flip", "0.40", "standing on dry cracked bare earth", "dry cracked earth",
            "low golden sun", "warm low sunlight"),
    "j21": ("headsq", "0.40", "standing against a pale open sky", "a pale sky",
            "low golden sun", "warm low sunlight"),

    # ── THE STRENGTH SWEEP. Same init, same ground clause and same light as the
    # framing's own sample cell, so the ONLY thing that moves inside a row is the
    # strength. A cell that passes the E-bar here is a dataset frame like any
    # other -- the sweep is not a throwaway.
    "k01": ("full", "0.35", "standing on dry cracked bare earth, a green hedgerow far behind",
            "dry cracked earth", "low golden sun", "warm low sunlight"),
    "k02": ("full", "0.30", "standing on dry cracked bare earth, a green hedgerow far behind",
            "dry cracked earth", "low golden sun", "warm low sunlight"),
    "k03": ("cowboy-flip", "0.30", "standing on dry cracked bare earth", "dry cracked earth",
            "low golden sun", "warm low sunlight"),
    "k04": ("cowboy-flip", "0.25", "standing on dry cracked bare earth", "dry cracked earth",
            "low golden sun", "warm low sunlight"),
    "k05": ("cowboy-flip", "0.20", "standing on dry cracked bare earth", "dry cracked earth",
            "low golden sun", "warm low sunlight"),
    "k06": ("headsq", "0.25", "standing against a pale open sky", "a pale sky",
            "low golden sun", "warm low sunlight"),
    "k07": ("headsq", "0.20", "standing against a pale open sky", "a pale sky",
            "low golden sun", "warm low sunlight"),
    "k08": ("headsq", "0.15", "standing against a pale open sky", "a pale sky",
            "low golden sun", "warm low sunlight"),

    # ── SWEEP ROUND TWO. The full-body row continues down after the pupil; the
    # native square gets the bracket its predecessor's failure defined.
    "m01": ("full", "0.25", "standing on dry cracked bare earth, a green hedgerow far behind",
            "dry cracked earth", "low golden sun", "warm low sunlight"),
    "m02": ("full", "0.20", "standing on dry cracked bare earth, a green hedgerow far behind",
            "dry cracked earth", "low golden sun", "warm low sunlight"),
    "m03": ("headnat", "0.30", "standing against a pale open sky", "a pale sky",
            "low golden sun", "warm low sunlight"),
    "m04": ("headnat", "0.25", "standing against a pale open sky", "a pale sky",
            "low golden sun", "warm low sunlight"),
    "m05": ("headnat", "0.20", "standing against a pale open sky", "a pale sky",
            "low golden sun", "warm low sunlight"),
}

# THE POSITIVE. `a small green goblin` and nothing else about him -- the same
# subject noun round one used, which is the most the closure allows: it names a
# species and a colour that are already in the init's pixels and argues about no
# feature of his face. The quality tail is animagine's own and is byte-identical
# to round one's, so a difference between this route's frames and round one's is
# the ground and the light and not the wording.
POSITIVE_TMPL = ("a small green goblin %s, %s, detailed cinematic anime, "
                 "masterpiece, best quality, very aesthetic")

# Round one's negative, unchanged and carrying no face term at all.
NEGATIVE = ("lowres, worst quality, low quality, text, watermark, "
            "photorealism, 3d render, blurry, 2boys, multiple heads")

# THE CAPTION. Ten clauses, three of them variable, and the shape never moves.
CAPTION_TMPL = ("bnyjerry, 1boy, solo, standing, looking at viewer, %s, %s, "
                "%s, anime style, cel shading")

JUDGE = """JUDGED AT 1:1 AGAINST `taste/refs/goblin-canon-founder-0821.png`, ONE
FRAME AT A TIME, AND THE ADMISSION BAR IS HIS FACE. Nothing else is consulted --
not tile B, not a previous round, not a metric, not a contact sheet.

  E1 THE EYE. Narrow almond, off-white field, a TINY dark pupil, heavy upper
     lid. A large round iris of any colour is a FAIL. This is the axis four
     founder vetoes were spent on.
  E2 THE SKULL AND EARS. Broad low dome; smallish pointed ears sitting NEAR
     HORIZONTAL. A tall egg skull with large upswept ears is the vetoed design.
  E3 SMOOTH FACE. No brow furrows, no nasolabial folds, no jowls.
  E4 PALETTE. Desaturated sage, washed and high-key. Saturated kelly green is
     the vetoed palette.
  E5 COSTUME. The shirt with its placket, dark shorts, dark boots. (Not scored
     on the square portrait, where only the collar is in frame.)

  D1 DID THE CELL'S OWN AXIS ARRIVE? The caption will tell the trainer this
     frame stands on `<ground>` in `<light>`. If the ground did not change, the
     frame is DROPPED -- it is not re-captioned as grass, because a set of
     near-duplicates all captioned `tall grass` is the monoculture this batch
     exists to prevent, and a caption that describes a frame that did not
     arrive is a lie the LoRA will learn.
  D2 IS IT CLEAN? A second figure, a melted hand, a text artifact, a soft or
     smeared frame: dropped. A character set is small enough that one bad frame
     is 3% of everything the token learns.

ADMISSION IS MERCILESS AND THE TARGET IS >= 20 OF 32 ACROSS ALL THREE FRAMINGS.
A framing that admits nothing is reported as such rather than back-filled from
another framing -- the whole point of the set is that it is not one camera."""


def caption_for(cell: str) -> str:
    init, _s, _gc, ground_word, _lc, light_word = CELLS[cell]
    return CAPTION_TMPL % (INITS[init][2], ground_word, light_word)


def positive_for(cell: str) -> str:
    _i, _s, ground_clause, _gw, light_clause, _lw = CELLS[cell]
    return POSITIVE_TMPL % (ground_clause, light_clause)


def _sha(rel: str) -> str:
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def emit(cell: str, write: bool) -> str:
    init_key, strength, _gc, _gw, _lc, _lw = CELLS[cell]
    init_file, size, _framing = INITS[init_key]
    mask_file = "fullframe-mask-%dx%d-0822.png" % size
    init_sha = _sha("%s/%s" % (SRC_DIR, init_file))
    mask_sha = _sha("%s/%s" % (SRC_DIR, mask_file))
    # SEEDS DO NOT COLLIDE ACROSS THE TWO LETTER SERIES. `int(cell[1:])` alone
    # would give j01 and k01 the same draw, and the sweep's whole job is to be
    # comparable to the sample cell it descends from -- comparable, not identical.
    seed = SEED0 + int(cell[1:]) + {"j": 0, "k": 100, "m": 200, "n": 300, "p": 400}[cell[0]]

    new_id = "ep2-jds-%s-0822" % cell
    dirtok = "jds-%s-0822" % cell
    positive = positive_for(cell)
    caption = caption_for(cell)

    n_pos = assert_under_clip77("%s prompt" % new_id, positive)
    n_neg = assert_under_clip77("%s negative" % new_id, NEGATIVE)
    # THE CLOSURE, OVER THREE STRINGS AND NOT TWO. Round one had no captions to
    # check; a caption is exactly where a face word would do the most damage,
    # because it is the one string the TRAINER reads.
    assert_no_face_terms(new_id, positive, NEGATIVE)
    assert_no_face_terms("%s caption" % new_id, caption, "")

    fetch = '''#!/usr/bin/env python3
"""Fetch this cell's INIT and its full-frame mask, both by sha256.

The init is a cut of taste/refs/goblin-canon-founder-0821.png -- the picture the
founder selected with "dude, this is how the goblin should look" -- made by
pipeline/lora/build_jerry_inits_0822.py. It is refused on any mismatch, which
matters more here than anywhere else in this tree: the init IS the canon, and
every frame of the goblin LoRA's training set descends from these bytes.

THE URLS ARE WRITTEN OUT IN FULL RATHER THAN BUILT FROM A BASE + A PATH, and
that is for a reader that is not human: derive_fetch_guard scans the emitted
spec for `raw.githubusercontent.com/.../farm-out/<dir>/` and can only see a URL
whose host and path are adjacent in the text. A concatenated URL makes the guard
answer "no fetch URL found" -- the one answer it must never give -- and the
guard is what stands between this job and a 404 after the card is claimed."""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\%s"
UA = {"User-Agent": "banyan-city-jds/1.0 (albert.numbro@gmail.com)"}
WANT = {
    "%s": ("%s", "%s"),
    "%s": ("%s", "%s"),
}

os.makedirs(OUT, exist_ok=True)
for name, (url, want) in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing.\\n   want %%s\\n   have %%s"
                 %% (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%s %%d bytes sha %%s OK" %% (name, len(raw), have), flush=True)
''' % (dirtok,
       init_file, RAW + "%s/%s" % (SRC_DIR, init_file), init_sha,
       mask_file, RAW + "%s/%s" % (SRC_DIR, mask_file), mask_sha)

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "the goblin-LoRA lane, 2026-08-22",
            "consumer": (
                "TRAIN-JERRY-V2, and nothing else. This frame is a candidate "
                "TRAINING IMAGE for the character LoRA that "
                "`goblin-i2i-route-0822.md` section 4 names as the only "
                "remaining route to a POSEABLE goblin. It is not a plate "
                "candidate for any beat, it is not judged against beat 13's "
                "staging, and review/ep2-ship-0821 is not touched. If it does "
                "not pass the E-bar at 1:1 it is dropped, not curated around."),
            "success": (
                "ONE %dx%d png at strength %s in which E1-E5 hold against his "
                "image at 1:1 AND the cell's own axis arrived (D1): the ground "
                "and the light the caption will claim are actually in the "
                "frame. A frame that holds his face and did not change is a "
                "near-duplicate of the init and is dropped, because 32 copies "
                "of one picture is not a dataset."
                % (size[0], size[1], strength)),
            "why": (
                "THE DATASET FACTORY, CELL %s. The img2img route is CLOSED as a "
                "posing route on a mechanism -- at strength <= 0.40 only the "
                "last s*N steps run, and global structure is decided in the "
                "high-noise steps that never execute, which is why the face "
                "survives and why a full-strength OpenPose skeleton could not "
                "bend a knee. What it can still do is re-light and re-ground "
                "him with his face intact at 5 s a frame for $0, and that "
                "makes it the only source of goblin training frames that are "
                "HIS PIXELS rather than animagine's guess at them.\n\n"
                "THIS CELL'S VARIABLES: init `%s`, ground `%s`, light `%s`. "
                "Framing and handedness come from the INIT because they cannot "
                "come from the prompt at this strength -- that is round two's "
                "measured finding and not a preference." % (cell, init_key,
                                                            _gw, _lw)),
        },
        overrides={
            "key:node": "002b-first-citizen",
            "key:priority": 55,
            "key:est_minutes": 3,
            "key:sample": cell in SAMPLE_CELLS,
            "payload:prompt.txt": positive,
            # THE NEGATIVE IS NOT OVERRIDDEN, AND THAT IS THE STATEMENT. It is
            # round one's, INHERITED -- derive_spec refuses a byte-identical
            # override precisely so an unchanged string is expressed as
            # inheritance rather than as a re-typed copy that can drift. It is
            # read back and asserted below, so "inherited" is verified and not
            # assumed.
            "payload:fetch_init.py": fetch,
            "argv:--seed": str(seed),
            "argv:--strength": strength,
            "argv:--init-sha256": init_sha,
            "argv:--pad-crop": "0",
            "argv:--note": (
                "GOBLIN DATASET CELL %s. img2img from a cut of the canon "
                "image: init `%s` at %dx%d, strength %s, full-frame white "
                "mask (which is what makes the SDXL inpaint pipeline on base "
                "weights behave as plain img2img). Ground `%s`, light `%s`. "
                "This is a TRAINING FRAME candidate for the jerry v2 LoRA, "
                "not a plate for any beat."
                % (cell, init_key, size[0], size[1], strength, _gw, _lw)),
        },
        retoken=[(PARENT_DIRTOK, dirtok),
                 (PARENT_MASKTOK, mask_file[:-4]),
                 (PARENT_INITTOK, init_file[:-4]),
                 (PARENT_SEEDTOK, "s%d" % seed),
                 (PARENT_OUTTOK, "b13-jds-%s" % cell)],
        extra={
            "bar": JUDGE,
            "the_caption_this_frame_earns": (
                "%s\n\nWRITTEN BEFORE THE RENDER AND CONDITIONAL ON IT. If the "
                "frame is admitted this string is its caption verbatim; if the "
                "ground or the light did not arrive the frame is DROPPED. The "
                "caption is never edited to match a frame that missed -- that "
                "is how a dataset acquires a lie, and the trainer cannot tell "
                "the difference." % caption),
            "caption_scheme": (
                "TEN CLAUSES, THREE VARIABLE, IDENTICAL IN LENGTH ACROSS ALL 32 "
                "CELLS. `registry.yaml` v2b measured the rule: lengthening "
                "captions by two clauses cost identity 11/15 -> 9/15 and giving "
                "them back recovered it EXACTLY. Uniform length means the "
                "trigger's share of every caption in the set is the same.\n\n"
                "`standing`, `looking at viewer` and the framing word NEVER "
                "VARY AND ARE NAMED ANYWAY. A named attribute is one the token "
                "is excused from carrying, and the one thing this LoRA must not "
                "learn is a pose -- it exists so a skeleton can move him. A set "
                "cut from one standing picture and captioned without the word "
                "`standing` would fuse standing into `bnyjerry` and reproduce "
                "the img2img pose lock one level down."),
            "route_closure": (
                "pipeline/canon.yaml `route_closure_2026_08_22`. No face tag, "
                "no IP-Adapter scale, no reference re-crop. Checked in code by "
                "`derive_goblin_i2i_0822.assert_no_face_terms` over the "
                "positive, the negative AND the caption -- three strings, "
                "where round one had two."),
            "clip77_measured_not_estimated": (
                "positive %d of 77, negative %d of 77, on animagine's own "
                "vocab. The ground and light clauses are the HEAD of the "
                "positive rather than its tail on purpose: if a prompt ever "
                "overran, the quality tail would be what dropped and not the "
                "one thing this cell varies." % (n_pos, n_neg)),
            "camera_angle_is_not_an_axis": (
                "NAMED SO ITS ABSENCE IS NOT READ AS AN OVERSIGHT. `from "
                "below` and `high angle` are instructions about GLOBAL "
                "STRUCTURE and are decided in high-noise steps this pass never "
                "enters -- the same mechanism that made an OpenPose skeleton at "
                "scale 1.0 fail to bend a knee in round two. Angle variety in "
                "this set is geometry: the square head crop is a closer camera "
                "and the cowboy is a mid."),
            "post_ship_patch": (
                "review/ep2-ship-0821 IS NOT TOUCHED. Nothing here is a plate "
                "candidate for any beat."),
        },
        by="pipeline/derive_goblin_dataset_0822.py")

    # ── THE PARENT'S ANSWERS ARE NOT THIS CELL'S, AND ONE OF THEM WOULD HAVE
    # DISARMED THIS FILE'S OWN SAMPLE GATE.
    #
    # `ep2-b13-i2icanon-s30-0822` is a JUDGED spec: it carries `verdict_0822`
    # ("PICK"), plus round one's `is_candidate`, its bracket's `the_one_variable`
    # and its `round_2_lever`. derive_spec copies every key it is not told to
    # change, so a freshly emitted cell here would arrive carrying round one's
    # verdict -- and `sample_gate()` below admits a batch when every sample cell
    # has a key starting with `verdict`. The gate would have passed on three
    # specs that had never been rendered, which is the exact shape of failure
    # the gate exists to prevent, arriving through the gate itself.
    #
    # So they are POPPED, and the pop is asserted rather than attempted.
    for stale in ("verdict_0822", "is_candidate", "the_one_variable",
                  "round_2_lever", "the_rung_this_is_one_variable_from",
                  "failure_predicted_in_advance", "script_line"):
        child.pop(stale, None)
    left = [k for k in child if k.startswith("verdict")]
    if left:
        raise SystemExit("!! %s was emitted carrying a verdict key %r -- a spec "
                         "that has never rendered cannot be judged, and "
                         "sample_gate() reads exactly this key" % (new_id, left))

    # ── THE RETOKEN CHECK, ON TWO DIFFERENT SCOPES BECAUSE THE TOKENS ARE NOT
    # ALIKE. A leftover parent token is how a derived spec quietly renders into
    # the parent's directory or reads the parent's init.
    #
    # The DIRECTORY, OUTPUT and MASK tokens have no legitimate use anywhere in a
    # child, prose included, so they are swept over everything.
    #
    # The INIT token is different: `goblin-canon-founder-0821` is the name of the
    # founder's own picture, and both the fetch script's docstring and the
    # judging bar name it ON PURPOSE -- every init here is a cut of it and that
    # sentence is the provenance. Banning the word would delete the provenance to
    # satisfy a guard. It is therefore swept over the LOAD-BEARING surfaces only:
    # the command lines, the payload's file paths, and the artifact list. Those
    # are the three places where the string is a PATH rather than a fact.
    joined = repr({k: v for k, v in child.items() if k != "derivation"})
    for tok in (PARENT_DIRTOK, PARENT_OUTTOK, PARENT_MASKTOK):
        if tok in joined:
            raise SystemExit("!! %s still names the parent's %r" % (new_id, tok))
    load_bearing = repr([[s.get("argv", []) for s in child["steps"]],
                         sorted(child["payload"]),
                         child.get("artifacts", [])])
    if PARENT_INITTOK in load_bearing:
        raise SystemExit("!! %s carries the parent's init name %r on a command "
                         "line, a payload path or an artifact -- that is a "
                         "PATH that was not retokened, not provenance prose"
                         % (new_id, PARENT_INITTOK))
    names = [st["name"] for st in child["steps"]]
    if names.count("fetch") != 1:
        raise SystemExit("!! %s has %d fetch steps" % (new_id, names.count("fetch")))
    pay = child["payload"][r"C:\banyan-farm\%s\prompt.txt" % dirtok]
    neg = child["payload"][r"C:\banyan-farm\%s\negative.txt" % dirtok]
    if neg.strip() != NEGATIVE:
        raise SystemExit("!! %s inherited a negative that is not round one's:\n"
                         "   have %r\n   want %r" % (new_id, neg, NEGATIVE))
    assert_no_face_terms(new_id, pay, neg)
    argv = [t for s in child["steps"] for t in s.get("argv", [])]
    for flag, wantv in (("--strength", strength), ("--pad-crop", "0"),
                        ("--init-sha256", init_sha), ("--seed", str(seed))):
        got = argv[argv.index(flag) + 1]
        if got != wantv:
            raise SystemExit("!! %s: %s is %r want %r" % (new_id, flag, got, wantv))
    # THE INIT AND THE MASK MUST BE THE ONES THIS CELL NAMES. retoken rewrites
    # every string in the child, so a token that failed to match would leave the
    # PARENT's filename on the command line with THIS cell's sha256 beside it --
    # a mismatch the box would catch after claiming the card. Cheaper here.
    for flag, wantname in (("--init", init_file), ("--mask-png", mask_file)):
        got = argv[argv.index(flag) + 1]
        if not got.endswith("\\" + wantname):
            raise SystemExit("!! %s: %s is %r, want it to end in %r"
                             % (new_id, flag, got, wantname))

    out = "pipeline/jobs/%s.yaml" % new_id
    if write:
        derive_spec.write(child, out)
        # THE FETCH GUARD. The runner pulls the init over the wire from
        # raw.githubusercontent.com/.../main/; a file that is written, or
        # staged, or committed-but-unpushed passes every local test and 404s
        # the job after the queue has claimed the card.
        derive_fetch_guard.assert_fetch_urls_resolve(
            os.path.join(REPO, out), must_hold=(init_file, mask_file),
            log=lambda s: None)
        print("wrote %-38s init=%-12s s=%s seed=%d  %dx%d"
              % (out, init_key, strength, seed, size[0], size[1]))
    else:
        print("  %-5s init=%-12s s=%-5s seed=%-9d %4dx%-4d clip77 %d/%d"
              % (cell, init_key, strength, seed, size[0], size[1], n_pos, n_neg))
        print("        prompt : %s" % positive)
        print("        caption: %s" % caption)
    return out


def sample_gate() -> None:
    """`--batch` refuses until every sample cell has a judged verdict on disk.

    ONE SAMPLE BEFORE ANY BATCH, as a program. The three sample cells each carry
    ONE of this batch's three recipe changes; a `verdict*` key on a rendered
    spec is what "the founder looked at it" reduces to for a dataset frame,
    which is the same gate `derive_saplora_figplate_0822` uses.
    """
    import yaml
    missing = []
    for cell in SAMPLE_CELLS + SWEEP_CELLS + M_CELLS:
        p = os.path.join(REPO, "pipeline/jobs/ep2-jds-%s-0822.yaml" % cell)
        if not os.path.isfile(p):
            missing.append("%s: never emitted" % cell)
            continue
        spec = yaml.safe_load(open(p, encoding="utf-8"))
        if not any(k.startswith("verdict") for k in spec):
            missing.append("%s: emitted, no verdict key" % cell)
    if missing:
        raise SystemExit(
            "!! --batch REFUSED. ONE SAMPLE BEFORE ANY BATCH (founder, "
            "2026-08-03). Three sample cells for three recipe changes -- a "
            "non-grass ground (j01), a cropped and mirrored init (j14), an "
            "832x832 frame (j21) -- AND the strength sweep they forced, "
            "because two of the three came back with animagine's iris on his "
            "face and the cause was the crop. Not judged:\n"
            "   " + "\n   ".join(missing) + "\n"
            "   Render them (--sample --write, enqueue), judge each at 1:1 "
            "against his image, and write a `verdict_0822` key onto each spec.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--sample", action="store_true",
                    help="the three recipe-change cells and nothing else")
    ap.add_argument("--backfill", action="store_true",
                    help="re-draw the pupil-lottery drops at a new seed, and "
                         "the one cell that never fired")
    ap.add_argument("--sweep2", action="store_true",
                    help="sweep round two: the full-body row below 0.30, and "
                         "the native square that replaces the magnified one")
    ap.add_argument("--sweep", action="store_true",
                    help="the strength sweep the sample gate demanded: one "
                         "number per framing, one variable per cell")
    ap.add_argument("--batch", action="store_true",
                    help="the rest; refuses until the samples AND the sweep "
                         "are judged")
    ap.add_argument("--cell", default="", help="one cell by name")
    a = ap.parse_args()

    if a.cell:
        cells = [a.cell]
        if a.cell not in CELLS:
            print("!! no cell %r" % a.cell)
            return 1
    elif a.sample:
        cells = list(SAMPLE_CELLS)
    elif a.sweep:
        cells = list(SWEEP_CELLS)
    elif a.sweep2:
        cells = list(M_CELLS)
    elif a.batch:
        sample_gate()
        cells = [c for c in sorted(CELLS) if c.startswith("n")]
    elif a.backfill:
        cells = [c for c in sorted(CELLS) if c.startswith("p")]
    else:
        cells = sorted(CELLS)

    for cell in cells:
        emit(cell, a.write)

    if not a.write:
        n_full = sum(1 for c in CELLS if INITS[CELLS[c][0]][1] == (832, 1216))
        print("\n-- dry run, %d of %d cell(s). re-run with --write." % (len(cells), len(CELLS)))
        print("   inits    : %s" % ", ".join(sorted(INITS)))
        print("   grounds  : %d distinct" % len({CELLS[c][3] for c in CELLS}))
        print("   lights   : %d distinct" % len({CELLS[c][5] for c in CELLS}))
        print("   framings : %d portrait, %d at 832x1216" % (len(CELLS) - n_full, n_full))
        print("   negative : %s" % NEGATIVE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
