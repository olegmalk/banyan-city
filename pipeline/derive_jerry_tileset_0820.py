#!/usr/bin/env python3
r"""TWELVE TILE-FAITHFUL FRAMES IN TWELVE POSES, FOR THE JERRY LoRA SET.

WHY THIS IS A BATCH AND NOT A SAMPLE, argued rather than assumed, because the
standing rule is ONE SAMPLE BEFORE ANY BATCH. The rule is one sample per RECIPE
CHANGE. THE RECIPE HAS BEEN SAMPLED -- fourteen times tonight, one variable
each, $0: `ep2-b04-tileread-v0..v7-0820` found it and `ep2-b04-tilefix-w1..w6`
closed its two faults and showed it survives a seated, a running and a wide
body. Nothing in this file changes the recipe. What changes per job is the POSE,
which is the input the dataset is missing, and the founder's rule is not "never
render twelve things", it is "never scale a recipe nobody has looked at". This
one has been looked at, and the pictures are on /review/ep2-goblin-design-0819.

WHAT IS MISSING AND WHY IT BLOCKS TRAINING. `pipeline/lora/curation-tile-0820.yaml`
re-curated the existing 31-frame Jerry set against the B tile and found:
    15 REJECT (a human nose, human eyes, or both -- the whole beat-20 family)
     9 fail on THE EARS ALONE and are otherwise tile-faithful
     7 KEEP
and the seven sit in FOUR poses (b14 kneel x2 seeds, b15 sit x2, b19 seat x3).
Seven frames in four poses trains a POSE, not a character, and a pose-locked
character LoRA is worse than none because it appears to work on the beat it was
trained on and fails silently everywhere else. The nine near-misses cannot be
kept to pad the count: Danbooru has NO TAG for the tile's short low ear, which
makes the LoRA the only instrument that can teach it, which in turn means a
training set containing nine pairs of elf spikes teaches the exact defect the
LoRA exists to fix.

So the missing input is POSE BREADTH FROM A RECIPE THAT PASSES THE TILE BAR.
This is that: twelve poses, one seed each (seeds walk so the set is not
seed-degenerate), covering every action the seven-beat design wave needs plus
four camera/attitude variations a character LoRA wants.

THE RECIPE, verbatim from pipeline/canon.yaml `ep2-goblin-design-adult` ->
correction_2026_08_20, unchanged:

    masterpiece, best quality, very aesthetic, 1other, solo, colored skin,
    green skin, bald, <CLOAK>, blank eyes, tsurime, jitome, no nose,
    closed mouth, :|, expressionless, <POSE AND FRAMING>

<CLOAK> IS FRAMING-DEPENDENT AND THAT IS MEASURED, NOT STYLE: `ragged cloak` at
close-up, `patchwork cloak` at full body. At a head-and-shoulders crop the
largest surface in frame is the skull and `patchwork` paints it -- stitches and
a red patch on the head in six of eight wedge rungs. At full body the same tag
lands on the cloth (w4, w5). Negating it does not work (w1: the patch returned
frame-for-frame identical). Each pose below carries the cloak word its framing
calls for and says which.

WHAT THIS DOES NOT DO. It produces NO beat plate, nothing enters any cut, and no
frame here is a pick. Every output is a LoRA training CANDIDATE and every one
still has to clear T1-T4 by eye before it enters the manifest -- a recipe that
passed at one seed is not a promise about twelve.

Usage:  python3 pipeline/derive_jerry_tileset_0820.py [--write]
"""

from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402
import sd_prompt  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b04-tilefix-w2-0820.yaml"
PARENT_DIR_TOKEN = "b04tilefix-w2-0820"
PARENT_ID_TOKEN = "ep2-b04-tilefix-w2-0820"

QUALITY = "masterpiece, best quality, very aesthetic"
CORE = ("1other, solo, colored skin, green skin, bald, %s, "
        "blank eyes, tsurime, jitome, no nose, closed mouth, :|, expressionless")
NEGATIVE = (
    "lowres, worst quality, low quality, text, watermark, pointy ears, "
    "long pointy ears, elf, monster boy, pointy nose, dot nose, human face, "
    "wrinkled skin, old man, thick eyebrows, hair, beard, child, chibi, "
    "grey skin, pale skin, 2boys"
)

# (tag, cloak, pose+framing, seed, which beat or which LoRA need it serves)
POSES = [
    ("p01", "patchwork cloak", "running, leaning forward, in tall grass, full body",
     20260820, "beat 02's sprint"),
    ("p02", "patchwork cloak", "crouching, hiding behind a small plant, full body",
     20260821, "beat 03's bad cover"),
    ("p03", "ragged cloak", "close-up, portrait, looking to one side",
     20260822, "beat 04's footnote - the tightest crop in the episode"),
    ("p04", "patchwork cloak", "standing, arms at sides, in tall grass, full body",
     20260823, "beat 07, being pointed at - the body, not the guard"),
    ("p05", "patchwork cloak", "standing, head lowered, looking down, full body",
     20260824, "beat 08's shame"),
    ("p06", "patchwork cloak", "sitting on grass, knees up, hugging own legs, full body",
     20260825, "beat 13's shade"),
    ("p07", "patchwork cloak", "crouching, holding a small round fruit in both hands, full body",
     20260826, "beat 20's evidence"),
    ("p08", "ragged cloak", "close-up, portrait, from side, profile",
     20260827, "LoRA needs a profile or it learns one camera"),
    ("p09", "ragged cloak", "close-up, portrait, looking up, from below",
     20260828, "LoRA needs a low angle"),
    ("p10", "patchwork cloak", "sitting on grass, cross-legged, full body, from behind, looking back",
     20260829, "LoRA needs the back of the skull"),
    ("p11", "patchwork cloak", "walking away, in tall grass, wide shot, full body, from behind",
     20260830, "beat 17's goodbye, which ships as a back view"),
    ("p12", "patchwork cloak", "kneeling, both hands on knees, in tall grass, full body",
     20260831, "beat 14 and beat 19, the two poses already in the set"),
]

BAR = """EVERY FRAME IS A CANDIDATE, NOT A PICK, AND CLEARS THE SAME FOUR
CLAUSES BY EYE BEFORE IT ENTERS THE MANIFEST -- read at 1:1 against
review/ep2-goblin-design-0819/adult-b19-0819.jpg:
  T1 EYES  blank white, no iris, no pupil.
  T2 NOSE  no bridge, no tip, no drawn nostrils.
  T3 AGE   no brow furrows, no folds, no jowls.
  T4 EARS  short and low if visible. LONG TAPERING SPIKES ARE A REJECT, and on
           this set that is not a style note: the LoRA exists to teach an ear
           Danbooru cannot name, so one spiked frame in the set teaches the
           spike.
  T7 SKIN IS NOT A COSTUME. No stitches, seams or patches on the head or face.
T5 (dome) and T6 (two-tone) are NOT scored. T6 was STRUCK from the tile bar on
2026-08-20 -- rung w3 proved `two-tone skin` renders as two discrete regions (a
magenta half-head), so the tile's falloff is rendered light and asking for it
manufactures a defect.
A FRAME THAT FAILS ANY OF T1-T4 OR T7 IS DROPPED, NOT FIXED. There are twelve
here and the set does not need all twelve."""

PREDICTED = """THE CLOSE-UPS ARE THE RISK AND THE FULL BODIES ARE NOT. Every
full-body rung tonight held the face (w4 seated, w5 running, w6 wide), so p01,
p02, p04-p07, p10-p12 are predicted to pass T1-T3 and to be UNSCORABLE on T4
because the ear will be a few pixels. An unscorable pass tells us nothing about
the ear, which is the attribute the LoRA is for -- so THE THREE CLOSE-UPS (p03,
p08, p09) CARRY THE EAR EVIDENCE ALONE, and if they fail, the set trains
everything except the one thing no prompt can say.
THE TWO MOST LIKELY INDIVIDUAL FAILURES, named so they are not explained away:
p09 (looking up, from below) because a low angle puts the jaw and the underside
of the skull in frame and nothing tonight has tested that geometry; and p10
(from behind, looking back) because a turned head is where identity drift lives
in every i2v result this tree has produced.
IF FEWER THAN SIX PASS, the wording route has reached its ceiling for dataset
purposes and the honest next instrument is IP-Adapter conditioned on the tile
itself -- slower, and not to be reached for before this is measured."""


def patch_publish(child):
    for step in child.get("steps") or []:
        step["argv"] = [a.replace("-hintskel.png", "-nocontrol.png")
                        if isinstance(a, str) else a
                        for a in step.get("argv") or []]
    child["artifacts"] = [a.replace("-hintskel.png", "-nocontrol.png")
                          if isinstance(a, str) else a
                          for a in child.get("artifacts") or []]
    return child


def main() -> int:
    write = "--write" in sys.argv
    bad = []
    for tag, cloak, pose, seed, serves in POSES:
        token = "jerrytile-%s-0820" % tag
        new_id = "ep2-jerry-tileset-%s-0820" % tag
        prompt = "%s, %s, %s" % (QUALITY, CORE % cloak, pose)
        n = sd_prompt.negative_tokens(prompt)
        if n > 77:
            bad.append("%s prompt = %d" % (tag, n))
        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "goblin-design audit lane, 2026-08-20 night",
                "consumer": (
                    "THE JERRY LoRA TRAINING SET. "
                    "pipeline/lora/curation-tile-0820.yaml re-curated the "
                    "existing 31 frames against the B tile and kept SEVEN, in "
                    "four poses, and refuses to file training on a set that "
                    "would teach a pose instead of a character. This job is one "
                    "of twelve poses filling that gap. It is a training "
                    "CANDIDATE and not a pick: no beat plate, nothing in any "
                    "cut, and it still has to clear T1-T4 and T7 by eye before "
                    "it enters any manifest."),
                "success": (
                    "ONE 832x1216 png of the tile-faithful creature in the pose "
                    "%r (%s), at seed %d. The identity clause and the negative "
                    "are byte-identical to the ratified recipe in "
                    "pipeline/canon.yaml correction_2026_08_20; the POSE and "
                    "the cloak word are the only things that differ between the "
                    "twelve jobs, and the cloak word is set by the framing rule, "
                    "not by choice." % (pose, serves, seed)),
                "why": (
                    "POSE %s OF TWELVE, SERVING %s. The recipe was measured over "
                    "fourteen $0 samples tonight and is ratified in canon; what "
                    "the dataset lacks is bodies, not wording. `%s` is used here "
                    "because the framing is %s and the cloak word is "
                    "framing-dependent by measurement: at a tight crop "
                    "`patchwork` paints the SKULL (six of eight wedge rungs), at "
                    "full body it lands on the cloth. Negating it does not work "
                    "-- rung w1 added `scar, stitches` to the negative and the "
                    "patch returned frame-for-frame identical."
                    % (tag, serves, cloak,
                       "a close-up" if "close-up" in pose else "full body")),
            },
            overrides={
                "argv:--seed": str(seed),
                "payload:prompt.txt": prompt,
            },
            retoken=[(PARENT_DIR_TOKEN, token), (PARENT_ID_TOKEN, new_id)],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "the_one_variable": (
                    "The pose-and-framing clause. Identity clause, negative, "
                    "checkpoint, steps, cfg and size are identical across all "
                    "twelve; the seed walks so the set is not seed-degenerate; "
                    "the cloak word is a function of the framing and not a free "
                    "choice."),
                "one_sample_rule": (
                    "SATISFIED, and this is the one place in tonight's work "
                    "where the argument has to be made rather than pointed at. "
                    "The rule is one sample per RECIPE CHANGE and this file "
                    "changes no recipe -- it was sampled fourteen times tonight "
                    "(tileread v0-v7, tilefix w1-w6), the pictures are on "
                    "/review/ep2-goblin-design-0819, and w4/w5/w6 already "
                    "showed it survives a seated, a running and a wide body. "
                    "What varies here is the POSE, which is the missing dataset "
                    "input. Nothing is promoted and no beat is rendered."),
            },
            by="pipeline/derive_jerry_tileset_0820.py",
        )
        child = patch_publish(child)
        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        if write and not bad:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(derive_spec._dump(child))
        print("%-32s s%d %3d tok %s" % (new_id, seed, n,
                                        "written" if (write and not bad) else "(dry)"))
    if bad:
        print("!! past 77: %s" % "; ".join(bad))
        return 1
    if not write:
        print("\n-- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
