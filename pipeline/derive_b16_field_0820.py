#!/usr/bin/env python3
r"""BEAT 16, THE RESTAGE: four FIELD plates for the whole-sapling composite.

THE RESTAGE. `/review/ep2-b16-leaf-0820` put a real contradiction on the board:
the beat's brief asks for a leaf-as-subject macro ("Close on the sapling's leaf;
the scavenger sits blurred behind it") and the founder's own 08-17 canon entry
`sapling-cotyledon-shape` -- "the sapling 2 leaves are average leaves" -- rules
out any leaf drawn as a feature. Three wordings failed, a permutation test came
back negative, and the big-leaf composite that was built as evidence "does not
come out" (detail 10.45 -> 9.41 inside the region, and he is not blurred behind
it, he is gone). The coordinator lane logged the restage on 2026-08-20:

    CLOSE ON THE WHOLE CANON SAPLING, THE SCAVENGER BLURRED BEHIND IT.

Plant as subject, no leaf-silhouette feature. It keeps the brief's actual
relation -- the plant is the subject and he is depth -- and it obeys the canon
ruling instead of asking for an exception to it. THE FOUNDER'S CARD STAYS OPEN:
he can still say "licence" and nothing here forecloses it; these are plates, not
a cut, and beat 16 remains a slate until he screens something.

WHY A COMPOSITE AND NOT A PROMPT. The canon two-leaf sapling is NOT DRAWABLE BY
WORDS on this stack and that is measured, not felt: the strongest available
wording -- numeral plus explicit negation of every wrong count -- returned 0 of
16 frames with two leaves (Class A in pipeline/composite-init-pattern.md, no
continuous encoding for cardinality). The house instrument is composite-then-
inpaint, 4 for 4 on beats 19, 15, 03 and 13: draw the plant procedurally into a
plate with numpy/PIL, then ONE 0.30 pass to make it belong.

WHAT THIS SCRIPT FILES, AND WHAT IT DOES NOT. It files STEP 1 ONLY: four FIELD
plates by text, with NO PLANT IN THEM. The sapling is drawn in afterwards, off
the picked field, by a local $0 numpy pass, and the 0.30 finishing pass is a
separate one-job rung after that. Filing the field batch first is what makes the
composite step cheap to aim: the composite geometry has to be fitted to a
specific plate (b19's leaf tips are hard-coded to its plate for exactly this
reason), so picking the field BEFORE writing the geometry saves writing it four
times.

THE FOUR VARIANTS DIFFER IN FIELD AND FRAMING AND IN NOTHING ELSE. Every job
carries the same subject clause and the same depth clause; the seed walks so the
set is not seed-degenerate. What a picked plate has to give the composite:
  * CLEAN GRASS IN THE NEAR FOREGROUND, lower-centre, big enough to hold a
    seedling at plate scale without painting over anything that matters;
  * HIM READABLE AS A SEATED FIGURE AND NOT AS A FACE. The brief says "blurred
    behind it" and the 0820 mac plates failed by giving his head the whole
    frame, sharp. Depth is asked for as depth here -- `depth of field, blurry
    background, out of focus` on him -- and no face tags are used at all,
    because a face that is doing its job in this shot is out of focus.
  * A LOW CAMERA. Three of the four sit at ground level, because a seedling
    reads as the subject from a plant's own height and not from standing height.

THE GOBLIN DESIGN IS DELIBERATELY NOT ASKED FOR HERE AND THIS LANE STAYS OFF IT.
The peer lanes own the creature-vs-adult question tonight. The subject clause is
the ratified core minus every face tag (`blank eyes, tsurime, jitome, no nose,
closed mouth, :|, expressionless` are all dropped) -- not to dodge canon but
because they describe a face this shot does not show. Whatever the design lands
on, a blurred seated figure at this scale does not have to be re-rendered.

THE RECIPE IS UNCHANGED, so the one-sample rule is satisfied by the parent.
`ep2-b04-tilefix-w2-0820` is the ratified still recipe -- animagine-xl-3.1,
832x1216, `--arm nocontrol`, scale 0.45 -- sampled fourteen times on 2026-08-20
and already re-used at twelve poses for the Jerry tileset, all of which are on
disk in farm-out/. THE NEGATIVE IS CARRIED BYTE FOR BYTE and nothing is added to
it, including the plant words it would be tempting to add: negatives have failed
to hold position three for three on this tree, and the composite's mask covers
whatever the field puts in the foreground anyway.

$0, ~3 min each, ~12 min for the set.

Run:  python3 pipeline/derive_b16_field_0820.py [--write]
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402
import sd_prompt  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b04-tilefix-w2-0820.yaml"
PARENT_DIR_TOKEN = "b04tilefix-w2-0820"
PARENT_ID_TOKEN = "ep2-b04-tilefix-w2-0820"

QUALITY = "masterpiece, best quality, very aesthetic"
# Scenery first, then him, then depth. No face tags: the face is out of focus by
# design, and naming it is how the 0820 mac plates ended up as a head filling
# the frame.
FIELD = "scenery, tall grass, outdoors, day, sunlight"
SUBJECT = ("1other, solo, colored skin, green skin, bald, patchwork cloak, "
           "sitting")
DEPTH = "far away, depth of field, out of focus, blurry background"

# (tag, framing clause, seed, what this variant is FOR)
VARIANTS = [
    ("f1", "from below, wide shot, horizon", 20260841,
     "the default: camera at the seedling's own height, horizon high, the "
     "largest clean near-foreground of the four"),
    ("f2", "from below, wide shot, blue sky, clouds", 20260842,
     "the same low camera with the horizon dropped and sky behind him -- a "
     "seedling silhouetted against sky separates from the grass better than "
     "one silhouetted against more grass"),
    ("f3", "eye level, medium shot, dense tall grass", 20260843,
     "no sky at all and grass on every side, which is the framing that makes "
     "him hardest to mistake for the subject and the composite hardest to "
     "make belong -- both worth knowing"),
    ("f4", "from below, wide shot, sunbeam, backlighting", 20260844,
     "the lit variant: the composite pattern re-applies THE PLATE'S OWN "
     "shading field to the drawn plant, so a plate with a real light direction "
     "gives that step something to work with"),
]

BAR = """FOUR PLATES, JUDGED AS ONE CONTACT SHEET, BY EYE AT 1:1, AND AT MOST
ONE IS PICKED. This is a FIELD, not the shot: the plant is not here yet and its
absence is not a fault.
  F1 A CLEAN NEAR FOREGROUND, lower-centre, wide enough and tall enough to hold
     a seedling at plate scale. A blade of grass crossing it is fine -- a rock,
     a flower, a second creature or a drawn plant is not, because the composite
     would have to paint over a structure the 0.30 pass will fight to keep.
  F2 HE IS DEPTH, NOT THE SUBJECT. A seated figure, small, out of focus, read
     at a glance as "someone is sitting back there". IF HIS HEAD IS SHARP OR
     FILLS ANY LARGE PART OF THE FRAME THE PLATE IS OUT -- that is exactly how
     the 0820 mac plates failed, twice.
  F3 ONE FIGURE. Not two, not a crowd.
  F4 THE LIGHT HAS A DIRECTION and it is daytime. The composite step measures
     the plate's own low-pass luminance gradient and carries it into the drawn
     plant; a flat, directionless plate makes that step a no-op.
  F5 CEL, NOT PHOTO. Same dialect as the rest of the episode.
NOT SCORED: the goblin's design. He is out of focus on purpose and no face tag
was used. A plate is not rejected here for reading as the old design or the new
one -- if the creature ruling changes what a blurred seated figure looks like,
that is a re-render nobody has to do.
NOT SCORED: whether the shot works. That question needs the plant in it and it
belongs to the composite rung, not to this one."""

PREDICTED = """F1, THE CLEAN FOREGROUND, IS WHAT I EXPECT TO LOSE. `field of
tall grass` at 832x1216 puts blades everywhere by construction, and the near
foreground is exactly where a sampler likes to put its biggest, sharpest
blades. If all four come back with a busy lower-centre the fix is a framing
word, not a fifth field: `from below` with the horizon higher gives more
mid-ground and less near grass.
SECOND: HE COMES BACK SHARP ANYWAY. `depth of field, blurry, out of focus` is
asking a still model for a lens property, and the 0820 mac plates showed this
beat's specific gravity -- the goblin pulls focus here even when he is not asked
for. If two or more plates give him a sharp head, the next rung composites him
smaller rather than saying `blurry` louder.
THIRD, AND IT IS THE ONE THAT WOULD CHANGE THE ROUTE: A PLANT ARRIVES UNASKED.
`field`, `grass` and `outdoors` can summon a flower or a shrub into the near
foreground. That is not fatal -- the composite mask covers it -- but a plate
whose foreground already contains a plant makes the 0.30 pass argue with a
structure instead of finishing one, and f3 is the variant most exposed to it.
IF ALL FOUR FAIL F1 AND F2 TOGETHER, the honest read is that a text field plate
is the wrong input and the composite should be built on an EXISTING beat plate
that already has him seated at the right depth -- beat 15's or beat 13's, both
of which are on disk and both of which already carry a composited plant."""


def main() -> int:
    write = "--write" in sys.argv
    bad = []
    for tag, framing, seed, serves in VARIANTS:
        new_id = "ep2-b16-field-%s-0820" % tag
        token = "b16field-%s-0820" % tag
        prompt = "%s, %s, %s, %s, %s" % (QUALITY, FIELD, SUBJECT, DEPTH, framing)
        n = sd_prompt.negative_tokens(prompt)
        if n > 77:
            bad.append("%s prompt = %d tokens" % (tag, n))
        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "beat-16 restage lane, 2026-08-20 night",
                "consumer": (
                    "BEAT 16'S SLATE IN THE EPISODE 2 CUT, the last-but-one "
                    "empty slot. Three wordings and one big-leaf composite have "
                    "failed it, and the route logged on 2026-08-20 is the "
                    "RESTAGE: close on the whole canon sapling with the "
                    "scavenger blurred behind it. This plate is STEP 1 of that "
                    "route -- the field the sapling gets drawn into. Variant %s "
                    "of four; at most one of the four is picked and the other "
                    "three are evidence about the framing. NOTHING HERE ENTERS "
                    "THE CUT: a field plate with no plant in it is not the shot."
                    % tag),
                "success": (
                    "One 832x1216 png of an empty daylight grass field with the "
                    "scavenger SEATED AND OUT OF FOCUS in the distance, framed "
                    "%r, at seed %d. Judged by eye at 1:1 against five clauses: "
                    "F1 a clean near foreground in the lower centre big enough "
                    "for a seedling; F2 he reads as DEPTH, small and soft, not "
                    "as the subject -- a sharp head anywhere large is an "
                    "immediate reject and is how the 0820 mac plates failed "
                    "twice; F3 exactly one figure; F4 the light has a "
                    "direction, which the composite step measures and reuses; "
                    "F5 cel dialect. THERE IS NO PLANT IN THIS PICTURE AND "
                    "THAT IS CORRECT." % (framing, seed)),
                "why": (
                    "$0, ~3 minutes, and it is the cheapest half of the "
                    "restage. The composite instrument has to be fitted to a "
                    "SPECIFIC plate -- beat 19's leaf tips are hard-coded to "
                    "its plate -- so picking the field before writing the "
                    "geometry is the difference between writing that geometry "
                    "once and writing it four times. %s. The recipe is "
                    "unchanged from a still family sampled fourteen times on "
                    "2026-08-20 and already re-used across twelve Jerry "
                    "tileset poses, so a bad result here is attributable to "
                    "the words." % serves[0].upper() + serves[1:]),
            },
            overrides={
                "argv:--seed": str(seed),
                "payload:prompt.txt": prompt,
                "key:beat": 16,
                "key:est_minutes": 3,
                "key:script_line": (
                    'Beat 16 WHY (1:15-1:22), node.md verbatim: "Close on the '
                    "sapling's leaf; the scavenger sits blurred behind it.\" "
                    "RESTAGED 2026-08-20 to CLOSE ON THE WHOLE CANON SAPLING "
                    "with the scavenger blurred behind it -- the brief's own "
                    "relation (plant is subject, he is depth) with the "
                    "leaf-as-feature clause dropped, which is what "
                    "canon.yaml sapling-cotyledon-shape requires. The VO line "
                    'is UNCHANGED: "He talks to me because I\'m the only thing '
                    "here that won't file a report. Buddy, I wish I could. I "
                    'can\'t even wave."'),
                "key:script_authority": (
                    "Node 002b-first-citizen, live script `002b-t0-c`, "
                    "`approved_by: founder`, `approved_on: 2026-08-03`. Beat "
                    "16's LINE is the founder's own 2026-08-19 word -- \"for "
                    "beat 16's line, lets keep 'I can't even wave'\" -- and is "
                    "untouched. What changes is the STAGING, which is a stage "
                    "direction. The restage was logged by the coordinator lane "
                    "on 2026-08-20 as the option that satisfies BOTH the brief "
                    "and the founder's own 08-17 canon ruling; his card "
                    "/review/ep2-b16-leaf-0820 stays open and he can still "
                    "answer `licence` instead, which nothing here forecloses."),
            },
            retoken=[(PARENT_DIR_TOKEN, token), (PARENT_ID_TOKEN, new_id)],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "the_one_variable": (
                    "THE PROMPT, and across the four jobs only its FRAMING "
                    "CLAUSE. The quality, field, subject and depth clauses are "
                    "byte-identical in all four; the seed walks so the set is "
                    "not seed-degenerate. THE NEGATIVE IS THE PARENT'S BYTE FOR "
                    "BYTE and nothing was added to it -- not even the plant "
                    "words, because this tree's negatives have failed to hold "
                    "position three for three and the composite's mask covers "
                    "the foreground regardless. Checkpoint, size, steps, cfg, "
                    "controlnet arm and scale are the ratified recipe's."),
                "why_no_face_tags": (
                    "The ratified core carries `blank eyes, tsurime, jitome, no "
                    "nose, closed mouth, :|, expressionless` and EVERY ONE IS "
                    "DROPPED here. Not a canon dodge -- they describe a face "
                    "this shot does not show. The brief asks for him BLURRED "
                    "BEHIND the plant, the two 0820 mac plates failed by "
                    "handing his sharp head the whole frame, and naming seven "
                    "face attributes is an instruction to draw a face. It also "
                    "keeps this lane off the creature-vs-adult question the "
                    "peer lanes own tonight: at this scale and this blur the "
                    "design barely reads, so whichever way that lands, a "
                    "picked field plate does not have to be re-rendered."),
                "the_plate_is_step_one_of_three": (
                    "STEP 1 OF THREE. (1) this field, by text, no plant in it. "
                    "(2) the canon two-leaf sapling DRAWN into the picked field "
                    "by a local numpy/PIL pass -- the b19/b03/b13 instrument, "
                    "procedural and not a photograph, fitted to the object and "
                    "not to the mask, with the plate's own measured light "
                    "carried into it -- then ONE 0.30 inpaint to make it "
                    "belong. (3) one i2v motion sample off the finished plate, "
                    "with the scavenger's blur stated as depth. Steps 2 and 3 "
                    "are separate rungs with their own specs; this job is not "
                    "any of them and must not be read as one."),
                "init_provenance": (
                    "NONE, and that is the point: this is a text-to-image "
                    "plate with no init and no plant. The canon sapling arrives "
                    "in step 2 as drawn geometry, not as a sample, which is the "
                    "whole reason the composite instrument exists -- the "
                    "strongest wording available returned 0 of 16 frames with "
                    "two leaves."),
                "one_sample_rule": (
                    "SATISFIED BY THE PARENT. The rule is one sample per RECIPE "
                    "CHANGE and no recipe changes here: "
                    "ep2-b04-tilefix-w2-0820 is the ratified still recipe, "
                    "sampled fourteen times on 2026-08-20 (tileread v0-v7, "
                    "tilefix w1-w6) with the pictures on "
                    "/review/ep2-goblin-design-0819, and it has already been "
                    "re-used unchanged across twelve Jerry tileset poses that "
                    "are on disk in farm-out/. What varies here is the words, "
                    "and four framings of one field is the plate batch "
                    "episode-loop-v2 step 1 asks for."),
                "not_done_on_purpose": (
                    "No plant is prompted -- it cannot be drawn by words and "
                    "asking would only put a wrong plant in the way of the "
                    "right one. No face tags. No negative edit. No canon edit: "
                    "sapling-cotyledon-shape is OBEYED here, not amended, and "
                    "the licence option the founder was offered is still his to "
                    "take. No cut change: beat 16 stays a slate. No edit to "
                    "node.md, and none to pipeline/beat16_leaf_composite.py or "
                    "ep2-b16-leafcomp-0820, which belong to the lane that "
                    "built the big-leaf evidence."),
            },
            by="pipeline/derive_b16_field_0820.py",
        )
        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        if write and not bad:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(derive_spec._dump(child))
        print("%-26s seed %d  %3d tok  %s"
              % (new_id, seed, n, "written" if (write and not bad) else "(dry)"))
    if bad:
        print("!! past 77: %s" % "; ".join(bad))
        return 1
    if not write:
        print("\n-- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
