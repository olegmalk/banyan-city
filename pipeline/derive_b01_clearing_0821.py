#!/usr/bin/env python3
r"""BEAT 01, THE NO-HORIZON CELL: a receding feature that is a PLACE, not a landform.

WHAT THIS CELL IS AND WHY IT IS ONE CELL AND NOT A LADDER. The sapling-field
lane closed after four rounds having established the rule this beat needs
(review/ep3-sapling-dataset-0821/plates-0821.yaml):

    A SCENE CLAUSE THAT NAMES ONLY GROUND COVER RETURNS A MACRO OF THAT GROUND
    COVER, AT ANY FRAMING. What buys a drawable ground plane is a LANDFORM or a
    RECEDING FEATURE -- something the picture has to be positioned relative to.

Two rounds on beat 01 re-derived exactly that at a cost of four plates:
ep2-b01-field s1-s3 named `scenery` and came back as sunset vistas; r2s1
dropped it, named only ground cover, and came back as the macro grass wall the
rule predicts. Both are in pipeline/derive_b01_field_0821.py with their
pictures. This file does not run a third round of that question.

WHAT IS ACTUALLY OPEN IS ONE CELL THE CLOSED LADDER NEVER RAN. Every passing
cell it found bought its depth from a LANDFORM plus a sky: `distant hills,
clear sky`, `a treeline in the distance`, `distant misty mountains`, `a dirt
path` (which returned a forest avenue). Beat 01's approved look has NO SKY AND
NO HORIZON -- it is an intimate hazy field, and the founder approved that look
on 2026-08-21 by keeping the take that carries it. A landform cell cannot serve
it, because a landform IS a horizon.

So the cell is the other half of the rule, which the ladder states but never
tested alone: A RECEDING FEATURE THAT IS NOT A LANDFORM. A clearing in the
grass recedes -- the picture has to be positioned relative to it -- and it
brings no sky, no ridgeline and no treeline with it. It is also, unlike every
landform the ladder tried, A PLACE FOR THE STEM: the composite roots a vertical
stem at a measured point, and bare earth in a parting of the grass is that
point rather than something to stand near.

THREE LAWS ARE INHERITED FROM THE CLOSED LADDER AND NONE IS RE-TESTED:
  * `low angle` is OUT. Round 4's single controlled deletion took the batch
    from 1-of-8 straight horizons to 8-of-8. `wide shot` alone stays.
  * `scenery` is out of the positive AND banned in the negative. It is
    Danbooru's landscape-shot tag and it is what bought beat 01's round-1
    vistas three times out of three.
  * The negative is the parent's, untouched. This tree's negatives have failed
    to hold position four times; that is not the lever to pull, and a negative
    over 77 tokens bans NOTHING because the overflow is dropped from the tail.

GREEN IS A HARD REQUIREMENT, NOT AN AESTHETIC ONE. The ladder dropped u05, a
usable dry-tan plain, because beat16_sapling_composite samples the plant's
palette from the plate's OWN greens and crashed with no green-dominant pixel
anywhere in its lower half -- now a refusal with a reason, since inventing a
palette is decal tell #2 by definition. Beat 01's approved look is amber. Both
cells therefore name green explicitly, and the warm light is asked for as
LIGHT (`warm backlight`) rather than as a palette (`orange theme`), which is
the word that took round 1 to sunset.

THE TENSION THIS CELL DOES NOT RESOLVE, STATED RATHER THAN HIDDEN. The
inherited negative bans `bokeh, blurry, depth of field` -- the exact words that
make beat 01's shipping take hazy -- because on a subject-less prompt they
returned macro texture with no plane. So a plate that passes here will be
CRISPER than the take the founder approved. That is the right trade for a
compositing init (the composite needs a readable plane and the haze can be
graded), but it is a real difference and it is his call, not this lane's.

ROUND 1 RAN AND FIRED THE SECOND PRE-REGISTERED FAILURE EXACTLY. c01 came
back with a blue sky, a cloud band and a mountain range: `in the distance` is
what this checkpoint DRAWS AS A SKYLINE, whatever the thing in the distance is
said to be. The clearing never rendered as a feature at all -- the frame is
unbroken grass -- so the depth did not come from the named place, it came from
the horizon the model invented to hold the word `distance`.

EVERYTHING ELSE ON THE BAR PASSED, AND WELL: a straight horizon, a flat
rootable plane across the lower two-thirds, green-dominant throughout, clean
cel dialect, no plant and no figure. Per this file's own bar that makes it a
FAIL for beat 01 and a PASS for the sapling dataset, so the plate is HANDED
OVER rather than deleted -- it is a better ground plane than several the closed
ladder kept.

c02 IS WITHDRAWN UNRUN. Its clause is `a clearing of bare earth receding into
the distance`, which carries the exact word c01 just proved buys a skyline.
Running it would spend the last round re-measuring a closed question with a
warm light on top.

SO ROUND 2 CHANGES THE ONE THING THAT PUTS SKY IN THE FRAME: it stops asking
for distance and NAMES WHAT OCCUPIES THE FAR GROUND INSTEAD. `tall grass
closing in behind it` bounds the clearing with grass rather than opening it to
a horizon, which is beat 01's actual composition -- near grass, a lit gap, far
grass, no sky. The clearing stays; only the thing behind it changes.

ROUND 2 RAN, BOTH CELLS MISSED, AND THE THREE PLATES TOGETHER ARE ONE CLEAN
MECHANISM. THE ROUTE IS CLOSED ON THIS CHECKPOINT.

  c01  `a small clearing of bare earth IN THE DISTANCE`
       -> blue sky, cloud band, mountain range. Perfect eye-level plane.
          No clearing drawn at all.
  d01  `a small clearing of bare earth, TALL GRASS CLOSING IN BEHIND IT`
       -> sky GONE and the clearing DRAWN, both clauses bought. But the
          camera went with the horizon: it is a plan view looking DOWN into
          a grass mat, and the clearing is a hole in it. Nothing to stand a
          vertical stem on.
  d02  d01 + `warm backlight`
       -> the r03/r04 death, pre-registered here and fired: a radial
          starburst of lit blades around a central glow. No clearing, no
          plane, no ground.

WHAT THE THREE SAY TOGETHER. On this checkpoint, at this size, on a
subject-less prompt, THE ONLY THING THAT BUYS AN EYE-LEVEL GROUND PLANE IS A
DISTANT OBJECT -- and a distant object is a horizon. Depth and horizon are not
two levers here, they are one. The closed ladder found the same thing from the
other side and never had to notice it, because every plate it wanted was
allowed to have a sky in it. Beat 01 is the first consumer that wants the one
without the other, and the answer is that this checkpoint does not separate
them: name the distance and you get a skyline (c01); take the distance away and
the camera tips over to find some other depth cue and gives you a plan view
(d01) or abandons the plane entirely (d02).

SO THIS STOPS, AS THE ROUND BUDGET SAID IT WOULD. Beat 01 keeps the fignonly
take it is shipping. The iteration waits for the LoRA era, and that is not a
shrug -- it is the specific fix for the specific failure. A subject LoRA puts a
KNOWN OBJECT AT A KNOWN SCALE in the frame, and a known object is a depth cue
that is not a landform. The whole reason these three plates have no depth
without a horizon is that there is nothing in them to judge distance against;
the sapling itself is that thing, and pipeline/lora/manifest-sapling.yaml is 26
frames from being able to draw it.

WHAT LEAVES THIS LANE WITH A HOME. c01 is a good plate and not a wasted one --
straight horizon, flat rootable plane across the lower two-thirds,
green-dominant, clean cel dialect, no plant, no figure. It fails only the
no-sky clause, which is beat 01's requirement and not the dataset's, so it goes
to the sapling dataset (farm-out/ep3-b01clearing-c01-0821/) rather than into
the rejected list. d01 and d02 are D2 rejects and are kept only as the evidence
above.

TOTAL COST OF THE BEAT-01 PLATE ROUTE: seven plates, about a minute of
otherwise-idle card, $0. Four of the seven (the ep2-b01-field rounds) were
spent re-deriving a rule that was already written down in
review/ep3-sapling-dataset-0821/plates-0821.yaml before this lane started, and
that half was avoidable by reading first. The three here were not: they answer
a question that file poses and never asked.

ROUND BUDGET: TWO, and the first is two cells at one seed each. If neither
round lands a plate with a rootable plane and no horizon, this stops: beat 01
keeps the fignonly take it is shipping and the iteration waits for the LoRA
era. Nothing here is proposed as a swap -- the founder reverted beat 01 by hand
on 2026-08-21.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402
from derive_sapling_field_0821 import (BAR, assert_under_clip77,  # noqa: E402
                                       stage_step)

# Round 4's control: the cleanest recipe the closed ladder produced, and the
# one that proved `low angle` was the fisheye. Everything except the scene
# clause is inherited from it byte for byte.
PARENT = "pipeline/jobs/ep3-sapfld4-u01-0821.yaml"
PARENT_DIRTOK = "sapfld4-u01-0821"

QUALITY = "masterpiece, best quality, very aesthetic, no humans"
FRAMING = "wide shot"   # `low angle` stays dropped -- round 4's finding

# (tag, seed, scene clause, what this cell is FOR)
# No sky noun in either. Green named in both, for the composite's palette
# sampler. The receding feature is a CLEARING in both -- c01 tests it cold,
# c02 tests whether beat 01's warm backlight survives on top of it.
VARIANTS = [
    ("d01", 20260963,
     "in a green field, a small clearing of bare earth, tall grass closing in "
     "behind it, day",
     "ROUND 2, ONE CLAUSE FROM c01. `in the distance` is deleted -- it is the "
     "measured cause of c01's skyline -- and the far ground is NAMED as grass "
     "so the model has something to put there other than sky. The clearing is "
     "unchanged. If this returns a bounded gap with grass behind it, beat 01 "
     "has its plate class and the depth cue is a PLACE rather than a horizon. "
     "If it returns macro grass, then bounding the clearing removed the only "
     "depth the cell had and the no-horizon route is closed on this "
     "checkpoint."),
    ("d02", 20260964,
     "in a green field, a small clearing of bare earth, tall grass closing in "
     "behind it, warm backlight, day",
     "d01 PLUS BEAT 01'S LIGHT, one variable. `warm backlight` is asked for as "
     "light and not as `orange theme`, which is the word that took beat 01's "
     "own round 1 to a sunset. This is the closer match to the shipping take "
     "if the plane survives it. Pre-registered risk unchanged from c02: "
     "backlight silhouettes the near grass and eats the plane, which is how "
     "the closed ladder's r03 and r04 both died."),
]


def build(tag, seed, scene, cell_why):
    new_id = "ep2-b01-clearing-%s-0821" % tag
    dirtok = "b01clearing-%s-0821" % tag
    prompt = "%s, %s, %s" % (QUALITY, scene, FRAMING)
    n_p = assert_under_clip77("%s prompt" % new_id, prompt)

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "the ship-repair lane, 2026-08-21",
            "consumer":
                "BEAT 01'S COLD OPEN, as an INIT for beat16_sapling_composite "
                "-- the canon two-leaf sapling drawn at FINAL SIZE so the "
                "motion model has nothing left to grow. The shipping take "
                "(01-cold-open-LTX-fignonly-s20260840) is 7 of 8 scored "
                "clauses and fails G5a because the sapling and the shaft are "
                "redrawn across the clip; its own verdict closed the "
                "prompt-side door and named plate-side as one of two routes "
                "left. This is that route's plate. NOT A SWAP: the founder "
                "reverted beat 01 by hand on 2026-08-21 and asked for more "
                "iteration; R4 is his and these are candidates for his look.",
            "success":
                "One 832x1216 png at seed %d, cel dialect, of %s at 'wide "
                "shot', with (1) NO HORIZON AND NO SKY -- a landform or a "
                "skyline is a FAIL here even though it passes for the dataset "
                "lane, because beat 01's approved look has neither; (2) a "
                "clean drawable ground plane in the lower centre, flat enough "
                "to stand a vertical stem on; (3) no plant and no figure; and "
                "(4) green-dominant pixels in the lower half, because "
                "beat16_sapling_composite samples the plant's palette from "
                "them and REFUSES a plate without them (the u05 drop). Judged "
                "by eye at 1:1 against the shipping take's own frame 0."
                % (seed, scene),
            "why":
                "%s\n\n$0 beyond ~10 GPU-seconds. THE ONE VARIABLE AGAINST THE "
                "PARENT IS THE SCENE CLAUSE. Round 4's u01 is the parent and "
                "everything else is its own byte for byte: the quality prefix, "
                "`no humans`, `wide shot` with `low angle` still dropped, the "
                "negative, the checkpoint, the size, the steps, the cfg, the "
                "nocontrol arm and its 0.45 scale." % cell_why,
        },
        overrides={
            "seed": seed,
            "payload:prompt.txt": prompt,
            "key:priority": 31,
        },
        retoken=[(PARENT_DIRTOK, dirtok)],
        by="pipeline/derive_b01_clearing_0821.py",
    )

    child["steps"].insert(0, stage_step(dirtok))
    child["bar"] = (
        BAR.replace("TEN PLATES", "TWO PLATES")
           .replace("nine siblings", "one sibling")
        + "\n\nAND ONE CLAUSE THE DATASET BAR DOES NOT CARRY, BECAUSE THIS "
          "PLATE IS FOR A BEAT AND NOT FOR A DATASET: NO HORIZON AND NO SKY. "
          "Every plate the closed ladder kept has one; beat 01's approved look "
          "has neither, so a clean plate with a ridgeline in it is a FAIL for "
          "this consumer and should be handed to the dataset lane rather than "
          "scored here.")
    child["the_one_variable"] = (
        "THE SCENE CLAUSE (%r). It names a receding feature that is NOT a "
        "landform -- the half of the closed ladder's rule that ladder stated "
        "but never tested on its own, because every cell it ran bought its "
        "depth from hills, a treeline, a creek or a path." % scene)
    child["this_cell"] = cell_why
    child["the_rule_this_inherits"] = (
        "From review/ep3-sapling-dataset-0821/plates-0821.yaml, four rounds "
        "and 26 plates: a scene clause naming only ground cover returns a "
        "macro of that ground cover at any framing, and what buys a drawable "
        "plane is a landform OR A RECEDING FEATURE. Beat 01's own two rounds "
        "re-derived the first half at a cost of four plates before that file "
        "was read. This cell tests the second half, which is the only form of "
        "the rule that can serve a look with no horizon in it.")
    child["what_beat_01s_own_two_rounds_cost"] = (
        "Four plates and about a minute of card, $0. Round 1 (s1-s3) named "
        "`scenery` -- Danbooru's landscape-shot tag -- and returned sunset "
        "vistas three for three. Round 2 (r2s1) deleted it and named only "
        "ground cover, and returned the macro grass wall the closed ladder's "
        "rule predicts. Both rounds were run before that ladder's laws were "
        "read, which is the avoidable half of the cost and is recorded as "
        "mine.")
    child["failure_predicted_in_advance"] = (
        "FIRST AND MOST LIKELY: A CLEARING IS NOT READABLE AS DISTANCE. Every "
        "depth cue the closed ladder found is an OBJECT with a silhouette -- "
        "hills, trees, a creek, a path. A clearing is an ABSENCE, and this "
        "checkpoint may have no way to place the camera relative to a hole in "
        "the grass. Then c01 comes back as macro grass, the no-horizon route "
        "is closed for this checkpoint, and beat 01 keeps fignonly.\n"
        "SECOND: THE CLEARING ARRIVES AND BRINGS A HORIZON ANYWAY, because "
        "`in the distance` is what the model draws as a skyline. That is a "
        "FAIL for this consumer and a PASS for the dataset lane, so the plate "
        "gets handed over rather than deleted.\n"
        "THIRD, ON c02 ONLY: `warm backlight` silhouettes the near grass and "
        "the plane goes black before the clearing is readable. That is "
        "precisely how the closed ladder's r03 (sunset) and r04 (mist) died, "
        "and if it happens here the light has to come from the grade rather "
        "than from the plate.\n"
        "FOURTH, AND IT WOULD BE THE EXPENSIVE ONE: the plate passes by eye "
        "and then beat16_sapling_composite refuses it for want of a "
        "green-dominant pixel, as it refused u05. Both cells name green for "
        "this reason, and the check is cheap and offline -- it should be run "
        "on the returned png BEFORE any composite is attempted.")
    child["clip77_measured_not_estimated"] = (
        "prompt %d of 77, counted offline on animagine's own vocab before this "
        "file was written; negative inherited from the parent unchanged." % n_p)
    return new_id, child


def main():
    write = "--write" in sys.argv
    out = []
    for tag, seed, scene, cell_why in VARIANTS:
        new_id, child = build(tag, seed, scene, cell_why)
        path = "pipeline/jobs/%s.yaml" % new_id
        if write:
            out.append(derive_spec.write(child, path))
            print("wrote %s  seed=%d  %s" % (path, seed, scene))
        else:
            print("would write %s  seed=%d  %s" % (path, seed, scene))
    if not write:
        print("\n(dry run -- pass --write)")
        return 0
    for p in out:
        derive_fetch_guard.assert_fetch_urls_resolve(
            p, must_hold=("controlnet_plate.py",))
    print("\nfetch guard: all %d spec(s) resolve" % len(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
