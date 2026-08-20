#!/usr/bin/env python3
r"""THE TILE-READ WEDGE: eight plates, one seed, one variable, and the variable
is the identity clause.

WHAT QUESTION THIS ANSWERS, AND IT IS NOT A TASTE QUESTION.
The founder ruled 2026-08-20 night that the goblin must read as the B TILE'S
CREATURE and that `adult` in `pipeline/canon.yaml` was steward drift
(`correction_2026_08_20`). The design axis is now FIDELITY TO
review/ep2-goblin-design-0819/adult-b19-0819.jpg. The post-ship wave is seven
beats (02 03 04 07 08 13 20) and NOT ONE OF THEM CAN BE AUTHORED until we own a
wording that puts the tile creature on the canvas on purpose. This wedge is that
wording, measured instead of asserted.

THE FINDING THIS IS BUILT ON, AND IT IS THE REASON A WORDING WEDGE IS THE RIGHT
INSTRUMENT AT ALL. The two tile-faithful frames in the shipping cut -- beat 19
(which IS the tile) and beat 15 (the next-best match) -- were BOTH rendered from
the SAME man-read string that produced beats 03, 04, 13 and 20:

    b19: "1boy, solo, lean wiry adult goblin man, green skin, bald head,
          patchwork cloak, kneeling in a sunny grassy field, ... " neg: "... close-up ..."
    b15: "... beside one seated lean adult goblin man in a patchwork cloak,
          solo, sunny grassy field, wide shot, ..."  neg: "... close-up ..."

Both are WIDE and both put `close-up` in the negative. So the phrase is not the
discriminator -- FRAMING IS. At distance animagine draws the face as a blank
mask and the creature read is a by-product of scale; the tighter the crop, the
more it resolves that mask into a detailed adult human male. Beat 04 is the
tightest crop in the cut and it is the worst offender in it.

THAT IS ALSO WHY WE CANNOT JUST SHOOT EVERYTHING WIDE. The shot specs ask for
close-ups (b04's own `done_when` is a face-fills-frame close-up whose whole
subject is the eyes). A recipe that only works at distance is not a recipe, it
is an avoidance. So the wedge is run AT THE CLOSE-UP, on purpose, at the hardest
framing this episode contains.

THE LADDER. Eight rungs. Everything is held constant -- seed 20260820, the
checkpoint, 40 steps, cfg 7.5, 832x1216, the scene clause, the quality tail and
ONE shared negative -- and the only thing that moves is the identity clause,
which grows by exactly one tile attribute per rung:

  v0  CONTROL, CLOSE   the current canon string. Predicted: an adult human male.
  v1  CONTROL, WIDE    the SAME string, wide. Predicted: the tile creature.
                       v0/v1 is the framing finding turned into a measured pair
                       inside this batch instead of an argument from memory.
  v2  NO MAN WORDS     close. `adult`, `man` and `lean wiry` deleted, nothing added.
  v3  + EYES           v2 + blank eyes / white eyes / no pupils.
  v4  + NOSE + MOUTH   v3 + no nose / thin lipless mouth.
  v5  + EARS + SKULL   v4 + no eyebrows / large bald cranium / short backswept ears.
  v6  + SKIN + AGE     v5 + colored skin / green skin / smooth skin.
  v7  1OTHER           v6 with `1boy` -> `1other, monster boy`.

ONE SAMPLE BEFORE ANY BATCH (founder, 2026-08-03) IS SATISFIED AND HERE IS THE
ARGUMENT, because this looks like eight renders and the rule says one. The rule
is one sample PER RECIPE CHANGE, and the thing it forbids is scaling an
unapproved recipe across a set of beats -- "the K recipe, chosen on the steward's
own metric, rendered across all fifteen beats". This is the opposite shape: eight
DIFFERENT recipes, ONE sample each, ONE beat, no beat rendered twice, and nothing
promoted anywhere. It is the shape of the canaries that rule blesses by name --
the step sweep and the shake A/B. Nothing here scales until a rung passes and the
founder sees the picture.

THE NEGATIVE IS HELD CONSTANT AND THAT IS A DELIBERATE CONFOUND, NAMED. The
shared negative already suppresses the man-read (`nose`, `wrinkles`, `hair`,
`adult man`) and the child-read (`child`, `chibi`) and beat 02's grey
(`grey skin`, `pale skin`). So v0 is NOT the recipe as it shipped -- it is the
current positive with tonight's negative. If v0 already passes, the answer is
"the negative did it" and the positive ladder is unnecessary, which is a cheaper
and better result than any rung. Written down before the render so a v0 pass
cannot be re-read afterwards as a win for something else.

WHAT IS DELIBERATELY NOT IN THIS WEDGE:
  * NO LoRA, NO IP-Adapter, NO ControlNet, NO reference set, NO init image. The
    `--control`/`--control-sha256`/`--scale` flags are carried byte-identical
    from the parent and are INERT on `--arm nocontrol`
    (controlnet_plate.py:592, every use is inside `if use_cn:`). Carried rather
    than deleted so the derivation stays one-variable against its parent.
  * NO second seed. Seed variance is a different question and mixing it in here
    would make every rung's result unattributable.
  * NO beat other than 04. The consumer is THE RECIPE, not the beat.

Usage:  python3 pipeline/derive_b04_tileread_0820.py [--write]
"""

from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b02-adultplate-s20260820-0820.yaml"
PARENT_DIR_TOKEN = "b02adultplate-s20260820-0820"
PARENT_ID_TOKEN = "ep2-b02-adultplate-s20260820-0820"
SEED = 20260820

HEAD = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                      capture_output=True, text=True).stdout.strip()

# ---------------------------------------------------------------- the wedge --
# Held constant in every rung. The scene is beat 04's and the quality tail is
# the one both tile-faithful plates in the cut used.
SCENE_CLOSE = ("crouching low in tall sunny grass, morning field, "
               "close-up, face fills the frame, looking to one side")
SCENE_WIDE = ("crouching low in tall sunny grass, morning field, "
              "wide shot, full body, looking to one side")
TAIL = "detailed cinematic anime, masterpiece, best quality, very aesthetic"

# ONE negative for all eight. Suppresses the man-read, the child-read and beat
# 02's grey, so the ladder measures what the POSITIVE clause is worth.
NEGATIVE = (
    "human face, human nose, nose, nostrils, nose bridge, adult man, old man, "
    "wrinkles, forehead wrinkles, nasolabial fold, jowls, beard, stubble, "
    "hair, white hair, bangs, eyelashes, iris, pupils, glasses, "
    "long pointy ears, elf, "
    "child, chibi, baby, toddler, cute, blush, round face, chubby, "
    "grey skin, pale skin, white skin, human skin, "
    "2boys, crowd, extra arms, extra fingers, deformed hands, "
    "text, watermark, photorealism, 3d render, low quality, deformed"
)

# The identity clause, and it is the only thing that moves.
CANON_STRING = "lean wiry adult goblin man, green skin, bald head, patchwork cloak"

RUNGS = [
    ("v0", "CONTROL, CLOSE - the canon string as it stands, at the hard framing",
     "1boy, solo, " + CANON_STRING, SCENE_CLOSE),
    ("v1", "CONTROL, WIDE - the same string at the framing that already works",
     "1boy, solo, " + CANON_STRING, SCENE_WIDE),
    ("v2", "NO MAN WORDS - adult/man/lean wiry deleted, nothing added",
     "1boy, solo, goblin, green skin, bald, patchwork cloak", SCENE_CLOSE),
    ("v3", "+ EYES - the loudest creature cue in the tile",
     "1boy, solo, goblin, green skin, bald, patchwork cloak, "
     "blank eyes, white eyes, no pupils", SCENE_CLOSE),
    ("v4", "+ NOSE and MOUTH",
     "1boy, solo, goblin, green skin, bald, patchwork cloak, "
     "blank eyes, white eyes, no pupils, no nose, thin lipless mouth",
     SCENE_CLOSE),
    ("v5", "+ EARS and SKULL - short backswept ears, NOT pointy ears",
     "1boy, solo, goblin, green skin, bald, patchwork cloak, "
     "blank eyes, white eyes, no pupils, no nose, thin lipless mouth, "
     "no eyebrows, large bald cranium, short backswept ears", SCENE_CLOSE),
    ("v6", "+ SKIN and AGE - the full tile clause",
     "1boy, solo, goblin, colored skin, green skin, bald, patchwork cloak, "
     "blank eyes, white eyes, no pupils, no nose, thin lipless mouth, "
     "no eyebrows, large bald cranium, short backswept ears, smooth skin",
     SCENE_CLOSE),
    ("v7", "1OTHER - the full tile clause with the human-male subject tag dropped",
     "1other, monster boy, solo, goblin, colored skin, green skin, bald, "
     "patchwork cloak, blank eyes, white eyes, no pupils, no nose, "
     "thin lipless mouth, no eyebrows, large bald cranium, "
     "short backswept ears, smooth skin", SCENE_CLOSE),
]

BAR = """PRE-REGISTERED BEFORE THE RENDER, read at 1:1 beside
review/ep2-goblin-design-0819/adult-b19-0819.jpg. Six clauses, and the first
four are what "the creature, not a man" means:
  T1 EYES      blank white, no iris and no pupil drawn.
  T2 NOSE      no bridge, no tip, no drawn nostrils.
  T3 AGE       no brow furrows, no nasolabial folds, no jowls. A smooth mask.
  T4 EARS      ear length under about a third of head height, low and swept
               back. LONG TAPERING SPIKES ARE A FAIL on this clause even though
               four beats in the shipping cut have them.
  T5 SKULL     large smooth dome; no neck reading as a distinct cylinder.
  T6 COLOUR    two-tone -- crown lighter than the muzzle. Reported, not scored:
               the tile's own two-tone may be a lighting artefact and no rung
               should be failed on it until that is settled.
PASS = the FIRST rung that takes T1-T4 at the close framing. T5/T6 reported.
NOT A CLAUSE, and stated so nobody scores it: whether the resulting creature is
GOOD. That is R4 and it is the founder's. This measures fidelity to a picture he
already ruled, which is a comparison anyone can check."""

PREDICTED = """v0 FAILS T1, T2 and T3 -- an adult human male face, which is the
defect as it ships. v1 PASSES T1-T3 on framing alone and is the control that
proves the ladder is measuring the close-up problem and not the checkpoint.
v2 STILL FAILS: `1boy` plus a bare `goblin` leaves the human-male anatomy prior
intact and animagine will fill in the eyes and nose it was never told to leave
out -- deleting `man` is predicted to be worth almost nothing on its own, and if
that is wrong it is the cheapest possible answer.
THE HIGHEST-YIELD SINGLE RUNG IS PREDICTED TO BE v3 (the eyes), because a
blank-eyed face reads non-human before any other feature is parsed.
THE MOST LIKELY WAY THE WHOLE LADDER FAILS: every rung comes back with a human
face wearing blank contact lenses -- the tags bind as SURFACE DECORATION on human
anatomy rather than as a different skull. If that is what eight rungs show, the
wording route for the close-up is CLOSED and the answer is a reference route (a
LoRA trained on tile-faithful frames, or IP-Adapter off the tile), which is a
larger and slower instrument and should not be reached for first."""


def main() -> int:
    write = "--write" in sys.argv
    made = []
    for tag, headline, identity, scene in RUNGS:
        token = "b04tileread-%s-0820" % tag
        new_id = "ep2-b04-tileread-%s-0820" % tag
        prompt = "%s, %s, %s" % (identity, scene, TAIL)
        child = derive_spec.derive(
            PARENT,
            new_id,
            fresh={
                "owner": "goblin-design audit lane, 2026-08-20 night",
                "consumer": (
                    "THE RECIPE, NOT THE BEAT. The seven-beat design wave "
                    "(02 03 04 07 08 13 20) cannot be authored until a wording "
                    "puts the B tile's creature on the canvas at a CLOSE-UP on "
                    "purpose. This rung is one sample of one candidate wording; "
                    "beat 04's plate is the test bed because it is the tightest "
                    "crop in the cut and therefore the hardest case. No beat is "
                    "re-rendered by this job and nothing is promoted."),
                "success": (
                    "ONE 832x1216 png for rung %s (%s). Identity clause: %r. "
                    "Everything else is byte-identical across all eight rungs -- "
                    "same seed %d, same negative, same scene clause, same "
                    "sampler numbers. Judged against the six-clause tile bar "
                    "pre-registered in this file BEFORE the render existed."
                    % (tag, headline, identity, SEED)),
                "why": (
                    "RUNG %s OF AN EIGHT-RUNG TILE-READ WEDGE. %s. The founder "
                    "ruled 2026-08-20 night that the goblin must read as the B "
                    "tile's CREATURE and that `adult` in canon was steward "
                    "drift; the design axis is now fidelity to "
                    "adult-b19-0819.jpg. Beat 19 IS that tile and beat 15 is "
                    "the next-best match in the cut, and BOTH were rendered "
                    "from the same man-read string -- wide, with `close-up` "
                    "negated. So framing, not wording, is what separates the "
                    "creature from the man today, and a recipe that only works "
                    "at distance is an avoidance rather than a recipe. This "
                    "ladder asks what the positive clause is worth AT THE "
                    "CLOSE-UP, one attribute at a time." % (tag, headline)),
            },
            overrides={
                "argv:--seed": str(SEED),
                "argv:--repo-commit": HEAD,
                "payload:prompt.txt": prompt,
                "payload:negative.txt": NEGATIVE,
            },
            retoken=[(PARENT_DIR_TOKEN, token),
                     (PARENT_ID_TOKEN, new_id)],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "init_provenance": (
                    "NONE, and that is the design. No init image, no mask, no "
                    "IP-Adapter, no reference set and no control hint: this is "
                    "txt2img so that the only thing on the canvas is what the "
                    "wording put there. --control/--control-sha256/--scale are "
                    "carried byte-identical from the parent and are INERT on "
                    "--arm nocontrol (controlnet_plate.py:592 -- every use is "
                    "inside `if use_cn:`), kept rather than deleted so the "
                    "derivation stays one-variable against its parent."),
                "the_one_variable": (
                    "THE IDENTITY CLAUSE. Seed, checkpoint, steps, cfg, size, "
                    "scene clause, quality tail and the whole negative are "
                    "identical in all eight rungs. Rung v1 additionally moves "
                    "the FRAMING and is labelled as the control that does so."),
                "one_sample_rule": (
                    "SATISFIED. The founder's 2026-08-03 rule is one sample per "
                    "RECIPE CHANGE and forbids scaling an unapproved recipe "
                    "across a set of beats. This is eight DIFFERENT recipes at "
                    "ONE sample each, on ONE beat, with nothing promoted -- the "
                    "shape of the step sweep and the shake A/B, not the shape "
                    "of the K recipe."),
            },
            by="pipeline/derive_b04_tileread_0820.py",
        )
        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        made.append((new_id, out, prompt))
        if write:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(derive_spec._dump(child))
        print("%-28s %s" % (new_id, "written" if write else "(dry)"))
        print("    %s" % prompt)
    if not write:
        print("\n-- dry run. re-run with --write to author %d specs." % len(made))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
