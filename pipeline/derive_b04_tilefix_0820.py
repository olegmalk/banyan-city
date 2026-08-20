#!/usr/bin/env python3
r"""SIX FOLLOW-ON RUNGS OFF v6, THE RECIPE THAT PASSED, AND ONE BUG FIX.

WHAT PASSED. `ep2-b04-tileread-v6-0820` took all four scoring clauses of the
tile bar at beat 04's close-up -- blank slit eyes under a heavy dark brow, NO
nose at all, one thin line mouth, and a short low rounded ear. Its recipe:

    masterpiece, best quality, very aesthetic, 1other, solo, colored skin,
    green skin, bald, patchwork cloak, blank eyes, tsurime, jitome, no nose,
    closed mouth, :|, expressionless, <framing>

Two things it did NOT settle, and one it created:
  * T5 the skull is ROUND rather than the tile's tall dome. Partial.
  * T6 the two-tone crown-to-muzzle gradient is absent, and v7 proved the
    `two-tone skin` tag does not supply it -- it painted a PINK PATCH instead.
    But v7 moved THREE tags at once (two-tone + shiny + no eyebrows), so the
    tag has not actually been tested on its own. w3 does that.
  * `patchwork cloak` PUTS PATCHWORK ON THE SKULL. Stitch marks and a red
    patch on the head in six of the eight rungs. A costume tag bleeding onto
    anatomy, found by looking rather than by looking for it. w1 and w2 are the
    two independent ways to kill it.

THE BUG THIS FILE ALSO FIXES, AND IT IS NOT COSMETIC. Every one of the eight
wedge renders succeeded rc=0 and every one of the eight JOBS finished rc=1: the
publish step inherited from the parent globs `<task>-hintskel.png` while
controlnet_plate.py names its output by `--arm`, i.e. `<task>-nocontrol.png`
(controlnet_plate.py:492). So the pictures were made, sat on the box, published
2 of the 4 files the step requires, and the queue reported eight failures. They
had to be copied off by hand. Every spec here names `-nocontrol.png` in both the
publish glob and `artifacts:`.

  >> THE SAME BUG IS IN THE SIX UNCOMMITTED ep2-b02-adultplate-* SPECS, which
  >> share the parent. They will render perfectly and publish nothing. Not
  >> touched here -- another lane's files -- but flagged in the ladder.

THE SIX RUNGS. v6's prompt is the base; ONE thing moves in each.

  DEFECT RUNGS -- close the two open faults:
    w1  the NEGATIVE gains `scar, stitches, patchwork skin`. Tests whether the
        skull patchwork can be suppressed without touching the costume. Note
        Ban et al.: a negative acts only after the positive draws the thing, so
        this is the weaker of the two routes and is run first precisely because
        it is the one that keeps the costume word intact.
    w2  `patchwork cloak` -> `ragged cloak`. Tests whether the costume NOUN is
        the cause. If w2 is clean and w1 is not, the word is the mechanism and
        the answer is vocabulary, not suppression.
    w3  `two-tone skin` added ALONE (v7 moved three tags at once). Isolates T6.

  BREADTH RUNGS -- does the recipe survive a different body?
    w4  the beat 13 action: seated, knees drawn up.
    w5  the beat 02 action: sprinting low through grass.
    w6  wide full-body, the framing the tile itself uses.

WHY THE BREADTH RUNGS ARE NOT "SCALING AN UNAPPROVED RECIPE". They render no
beat plate and nothing enters any cut. Their consumer is the LoRA dataset:
pipeline/lora/curation-tile-0820.yaml found only SEVEN tile-faithful frames in
the existing 31, in FOUR poses, and says in as many words that seven frames in
four poses trains a pose rather than a character. Pose breadth from a recipe
that passes the tile bar is the missing input, and w4/w5/w6 are one sample each
of three poses. If the recipe breaks on a running body, that is the finding and
the dataset question changes shape.

Usage:  python3 pipeline/derive_b04_tilefix_0820.py [--write]
"""

from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402
import sd_prompt  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b04-tileread-v6-0820.yaml"
PARENT_DIR_TOKEN = "b04tileread-v6-0820"
PARENT_ID_TOKEN = "ep2-b04-tileread-v6-0820"
SEED = 20260820

HEAD = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                      capture_output=True, text=True,
                      encoding="utf-8").stdout.strip()

QUALITY = "masterpiece, best quality, very aesthetic"
V6_IDENTITY = ("1other, solo, colored skin, green skin, bald, patchwork cloak, "
               "blank eyes, tsurime, jitome, no nose, closed mouth, :|, "
               "expressionless")
V6_SCENE = "in tall grass, close-up, portrait"
V6_PROMPT = "%s, %s, %s" % (QUALITY, V6_IDENTITY, V6_SCENE)
V6_NEGATIVE = (
    "lowres, worst quality, low quality, text, watermark, pointy ears, "
    "long pointy ears, elf, monster boy, pointy nose, dot nose, human face, "
    "wrinkled skin, old man, thick eyebrows, hair, beard, child, chibi, "
    "grey skin, pale skin, 2boys"
)
# w1's negative CANNOT be v6's plus three terms -- that measures 80 tokens
# against CLIP's 77 and the box would refuse it. So it is v6's negative MINUS
# `dot nose` PLUS `scar, stitches`, and that trade is named rather than hidden:
# w1 is therefore v6 plus two terms and minus one, not a clean single addition.
# `dot nose` is the term given up because it is the weakest of the three nose
# backstops (6,459 posts) and because v6 already draws NO nose at all, so it
# was suppressing nothing. `patchwork skin` is dropped outright -- the research
# established that inventing tag strings does not work, and it is not a tag.
NEG_PLUS_SCAR = V6_NEGATIVE.replace(", dot nose", "") + ", scar, stitches"

RUNGS = [
    ("w1", "DEFECT - negative gains scar/stitches/patchwork skin",
     V6_IDENTITY, V6_SCENE, NEG_PLUS_SCAR),
    ("w2", "DEFECT - `patchwork cloak` -> `ragged cloak`",
     V6_IDENTITY.replace("patchwork cloak", "ragged cloak"), V6_SCENE,
     V6_NEGATIVE),
    ("w3", "T6 - `two-tone skin` added ALONE, isolated from v7's other two tags",
     V6_IDENTITY + ", two-tone skin", V6_SCENE, V6_NEGATIVE),
    ("w4", "BREADTH - the beat 13 action, seated with knees drawn up",
     V6_IDENTITY, "sitting on grass, knees up, hugging own legs, full body",
     V6_NEGATIVE),
    ("w5", "BREADTH - the beat 02 action, sprinting low through grass",
     V6_IDENTITY, "running, leaning forward, in tall grass, full body",
     V6_NEGATIVE),
    ("w6", "BREADTH - wide full body, the framing the tile itself uses",
     V6_IDENTITY, "in tall grass, wide shot, full body", V6_NEGATIVE),
]

BAR = """THE SAME SIX-CLAUSE TILE BAR v6 PASSED, unchanged, read at 1:1 against
review/ep2-goblin-design-0819/adult-b19-0819.jpg:
  T1 EYES   blank white, no iris, no pupil, narrow and slanted.
  T2 NOSE   no bridge, no tip, no drawn nostrils.
  T3 AGE    no brow furrows, no folds, no jowls.
  T4 EARS   short, low, swept back. Long tapering spikes FAIL.
  T5 SKULL  large smooth dome, no neck. Reported; v6 scored PARTIAL (round,
            not tall) and nothing in this batch tries to move it.
  T6 COLOUR two-tone, crown lighter than the muzzle. Reported except on w3,
            where it is THE clause under test.
PLUS ONE NEW SCORED CLAUSE, because the wedge found the defect and a follow-up
that does not measure it is a waste of the card:
  T7 SKIN IS NOT A COSTUME. No stitch marks, no seams and no patches ON THE
     HEAD OR FACE. v6 has a red patch and two stitches on the skull. w1 and w2
     each pass or fail this outright; the other four report it.
FOR THE THREE BREADTH RUNGS the bar is T1-T4 AND T7 at a DIFFERENT body, and a
failure there is the more interesting result: it would mean the recipe is
pose-bound and the LoRA route is required rather than optional."""

PREDICTED = """w2 BEATS w1. The mechanism is the word: `patchwork` is a
texture-and-seams concept and the model is applying it to the nearest large
surface, which at a head-and-shoulders crop is the skull. Ban et al. (ECCV 2024,
arXiv:2406.02965) say a negative acts only AFTER the positive has drawn the
thing and can even summon it early, so negating `stitches` while still asking
for `patchwork` is asking the model to draw and then unpaint. If w1 comes back
clean anyway, that is a genuine surprise and worth more than the fix.
w3 FAILS T6 and the whole two-tone question dies with it. `two-tone skin` is
18,474 posts and, on v7's evidence, means DISCRETE REGIONS of two colours -- a
pink patch -- not a gradient. The tile's crown-to-muzzle falloff is almost
certainly RENDERED LIGHT, not a skin attribute, and if w3 confirms that then T6
should be struck from the bar rather than chased, because chasing it will keep
producing two-coloured heads.
THE BREADTH RUNGS ARE THE REAL RISK. v6's pass came at a crop where the face
occupies most of the frame; at full body the face is a few dozen pixels and the
model has been shown all night that it draws a mask at that size. So w4/w5/w6
are predicted to PASS T1-T3 easily and to be UNSCORABLE on T4 -- and the honest
reading of an unscorable pass is that it tells us nothing about the ear, which
is the attribute the LoRA exists to teach."""


def patch_publish(child, task):
    """Repoint the inherited publish glob and artifacts at the real filename.

    THE WEDGE'S EIGHT RENDERS ALL SUCCEEDED AND ALL EIGHT JOBS REPORTED FAILURE
    because of this one string. controlnet_plate.py:492 names its output
    `<task>-<arm>.png`, the arm here is `nocontrol`, and the publish step
    inherited a glob for `-hintskel.png` from a parent whose step happens to be
    NAMED hintskel while running `--arm nocontrol`. The step then published 2 of
    the 4 files it requires and exited 1. Fixed in both places that name it, so
    box_enqueue's artifact-is-named-by-a-step guard still holds.
    """
    for step in child.get("steps") or []:
        step["argv"] = [
            a.replace("-hintskel.png", "-nocontrol.png") if isinstance(a, str)
            else a for a in step.get("argv") or []
        ]
    child["artifacts"] = [
        a.replace("-hintskel.png", "-nocontrol.png") if isinstance(a, str)
        else a for a in child.get("artifacts") or []
    ]
    return child


def main() -> int:
    write = "--write" in sys.argv
    bad = []
    for tag, headline, identity, scene, negative in RUNGS:
        token = "b04tilefix-%s-0820" % tag
        new_id = "ep2-b04-tilefix-%s-0820" % tag
        prompt = "%s, %s, %s" % (QUALITY, identity, scene)
        for what, text in (("prompt", prompt), ("negative", negative)):
            n = sd_prompt.negative_tokens(text)
            if n > 77:
                bad.append("%s %s = %d tokens" % (tag, what, n))
        child = derive_spec.derive(
            PARENT,
            new_id,
            fresh={
                "owner": "goblin-design audit lane, 2026-08-20 night",
                "consumer": (
                    "w1/w2/w3: THE RECIPE. v6 passed the tile bar and left two "
                    "faults -- patchwork bleeding onto the skull, and an "
                    "untested two-tone tag. Every beat of the seven-beat design "
                    "wave will be authored off this wording, so a defect left "
                    "in it is a defect in seven plates. "
                    "w4/w5/w6: THE LoRA DATASET. "
                    "pipeline/lora/curation-tile-0820.yaml found only seven "
                    "tile-faithful frames among the existing 31, in four poses, "
                    "and refuses to file training on a set that would teach a "
                    "pose instead of a character. Pose breadth off a passing "
                    "recipe is the missing input."),
                "success": (
                    "ONE 832x1216 png for rung %s (%s). v6's prompt with ONE "
                    "thing moved. Seed %d, sampler numbers and everything else "
                    "byte-identical to v6. Judged against the seven-clause bar "
                    "pre-registered in this spec BEFORE the render existed."
                    % (tag, headline, SEED)),
                "why": (
                    "RUNG %s, FOLLOWING v6. %s. v6 took all four scoring "
                    "clauses of the tile bar at beat 04's close-up -- blank "
                    "slit eyes, no nose, a thin line mouth and a short low ear "
                    "-- which is the first time this tree has drawn the "
                    "founder's B tile creature on purpose at a tight crop. What "
                    "it left behind is a costume tag painting stitches and a "
                    "red patch ON THE SKULL, an unresolved two-tone clause that "
                    "v7 tested three-at-a-time and therefore did not test, and "
                    "no evidence at all that the recipe survives a different "
                    "body." % (tag, headline)),
            },
            # derive_spec refuses a payload override byte-identical to the
            # parent's, and it is right to: w1 moves ONLY the negative, so
            # passing its unchanged prompt would be asserting a change that is
            # not there. Only the strings that actually differ are overridden.
            overrides=dict(
                [("argv:--seed", str(SEED)),
                 ("argv:--repo-commit", HEAD)]
                + ([("payload:prompt.txt", prompt)]
                   if prompt != V6_PROMPT else [])
                + ([("payload:negative.txt", negative)]
                   if negative != V6_NEGATIVE else [])),
            retoken=[(PARENT_DIR_TOKEN, token), (PARENT_ID_TOKEN, new_id)],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "the_one_variable": (
                    "v6's exact prompt, negative, seed and sampler, with ONE "
                    "change: w1 the negative, w2 the costume noun, w3 one added "
                    "skin tag, w4/w5/w6 the action-and-framing clause only."),
                "publish_glob_fixed_here": (
                    "The parent's publish step globs `-hintskel.png` while "
                    "controlnet_plate.py:492 writes `<task>-<arm>.png` and the "
                    "arm is `nocontrol`. That one string made all eight wedge "
                    "renders succeed rc=0 and all eight jobs report rc=1, with "
                    "the pictures stranded on the box. Repointed here in both "
                    "the glob and `artifacts:`. THE SAME BUG IS LIVE IN THE SIX "
                    "UNCOMMITTED ep2-b02-adultplate-* SPECS."),
                "one_sample_rule": (
                    "SATISFIED. Six rungs, six different recipes-or-poses, ONE "
                    "sample each, nothing promoted, no beat plate produced and "
                    "nothing entering any cut. The breadth rungs render POSES, "
                    "not beats."),
            },
            by="pipeline/derive_b04_tilefix_0820.py",
        )
        child = patch_publish(child, new_id)
        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        if write and not bad:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(derive_spec._dump(child))
        print("%-28s %3d tok  %s" % (new_id, sd_prompt.negative_tokens(prompt),
                                     "written" if (write and not bad)
                                     else "(dry)"))
        print("    %s" % prompt)
    if bad:
        print("\n!! REFUSING TO WRITE -- past CLIP's 77: %s" % "; ".join(bad))
        return 1
    if not write:
        print("\n-- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
