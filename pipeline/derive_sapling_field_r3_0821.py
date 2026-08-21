"""Round 3 -- the depth cue is a NAMED DISTANT OBJECT, not the framing word.

WHAT ROUND 2's FIRST FOUR CELLS PROVED, one variable at a time.

  r01  meadow + `wildflowers in the distance`, day   PASS -- reproduces p09
  r02  the SAME cell with the wildflowers clause removed   FAIL D2 -- macro grass
  r03  meadow + sunset, long shadows (no distance clause)  FAIL D2 -- grass silhouette
  r04  meadow + morning mist, backlighting (no distance)   FAIL D2 -- grass silhouette

r01 IS THE CONTROL AND IT HELD, so round 1's single pass was not a seed lottery
and the framing finding is real. But r02 is the cell that actually explains the
mechanism, and it corrects round 2's own conclusion one rung further:

  IT IS NOT `wide shot` THAT BUYS A GROUND PLANE. IT IS NAMING SOMETHING FAR
  AWAY. r02 is r01 with `wildflowers in the distance` deleted and nothing else
  changed -- same framing words, same seed family, same everything -- and it
  collapsed straight back into magnified grass. `wide shot, low angle` with no
  distant object named reverts to exactly the macro failure `close-up` gave in
  round 1. The framing word never chose a camera distance in either round; the
  DISTANT SUBJECT did, and in p09 and r01 it arrived by accident inside a
  scene clause I wrote for a different reason.

So round 2's "freeze the framing" was right about what to keep and wrong about
why, and r03/r04 are the cost of that: two lighting cells that could not be
read because they had no depth cue and lost D2 before their light was scorable.

ROUND 3 PUTS AN EXPLICIT DISTANCE CLAUSE IN EVERY CELL and drops the
wildflowers. Flowers were doing two jobs at once -- supplying depth and
littering the near foreground with structures the composite would have to paint
over, which is r01's one remaining D2 weakness. A treeline, distant hills, a
receding path and a far creek all supply the depth without putting anything in
the lower centre. The lighting axis, unreadable in r03/r04, is re-run here on
cells that can actually be scored.

Scale still does NOT come from the sampler: it comes from cropping these plates
(beat 09, 2.157x LANCZOS, 105% of frame 1's high-frequency energy at f121).

Run:  python3 pipeline/derive_sapling_field_r3_0821.py [--write]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402
from derive_sapling_field_0821 import (BAR, assert_under_clip77,  # noqa: E402
                                       stage_step)

PARENT = "pipeline/jobs/ep3-sapfld2-r01-0821.yaml"
PARENT_DIRTOK = "sapfld2-r01-0821"

QUALITY = "masterpiece, best quality, very aesthetic, no humans"
FRAMING = "wide shot, low angle"   # still frozen, still p09's

# Every cell names something FAR AWAY. That is the variable r02 isolated.
VARIANTS = [
    ("t01", 20260931, "in a green meadow, a treeline in the distance, clear sky, day",
     "THE NEW CONTROL. r01's cell with the depth cue swapped from wildflowers "
     "to a treeline -- depth kept, near-foreground structures removed. If this "
     "passes, the composite gets the clean lower centre r01 never had."),
    ("t02", 20260932, "in a green meadow, distant hills, clear sky, day",
     "A SECOND DEPTH CUE at the same light. Two different distant objects "
     "holding the same cell is what separates 'a distant object works' from "
     "'the word treeline works'."),
    ("t03", 20260933, "in a green meadow, a treeline in the distance, sunset, orange sky",
     "THE LIGHTING CELL r03 COULD NOT ANSWER. Same warm light, now with a "
     "depth cue so the plate has a ground plane to score."),
    ("t04", 20260934, "in a green meadow, distant hills, morning, mist",
     "THE LIGHTING CELL r04 COULD NOT ANSWER. Mist over distant hills is also "
     "the cheapest test of whether haze eats the depth cue that buys the "
     "plane."),
    ("t05", 20260935, "in a green field, a dirt path receding into the distance, day",
     "DEPTH BY PERSPECTIVE rather than by a far object -- a path recedes by "
     "construction. It also hands the composite an unvegetated strip to root "
     "in, which is the D2 clause every failing cell has lost."),
    ("t06", 20260936, "in a green meadow, a treeline in the distance, overcast, soft light",
     "THE FLAT CELL, filed against D4 on purpose. If a directionless plate "
     "still yields a composite that belongs, the light-carry step is doing "
     "less than its docstring claims."),
    ("t07", 20260937, "in a field of dry grass, distant hills, autumn, clear sky",
     "PALETTE. The composite samples its greens FROM THE PLATE, so a plate "
     "with no green tests whether the instrument puts a green sapling in a dry "
     "field or tints it straw."),
    ("t08", 20260938, "in a green meadow, a shallow creek in the distance, clear sky, day",
     "TERRAIN, with the water pushed to the background instead of the "
     "foreground. Round 1's creek cell was the only near-miss on dialect, and "
     "this is that scene at the framing and depth that work."),
]


def build(tag, seed, scene, cell_why):
    new_id = "ep3-sapfld3-%s-0821" % tag
    dirtok = "sapfld3-%s-0821" % tag
    prompt = "%s, %s, %s" % (QUALITY, scene, FRAMING)
    n_p = assert_under_clip77("%s prompt" % new_id, prompt)

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "sapling-dataset lane, 2026-08-21 round 3",
            "consumer":
                "THE SAPLING LoRA DATASET's scene and lighting breadth. "
                "pipeline/lora/README.md wants >=20 composited saplings across "
                "distinct scenes, scales and lighting, and the ~23 that exist "
                "share five near-identical tall-grass scenes AND a figure. "
                "These are goblin-free ground planes with a depth cue, which "
                "is the thing rounds 1 and 2 measured as load-bearing. No cut, "
                "no beat, no promotion.",
            "success":
                "One 832x1216 png at seed %d, cel dialect, of %s at 'wide "
                "shot, low angle', with a CLEAN DRAWABLE GROUND PLANE in the "
                "lower centre, no plant and no figure. Judged by eye at 1:1 "
                "against the five D-clauses with its seven siblings."
                % (seed, scene),
            "why":
                "%s\n\nROUND 2 CORRECTED ITSELF AT r02. `wide shot, low angle` "
                "does not buy a ground plane -- naming something FAR AWAY "
                "does. r02 is r01 with `wildflowers in the distance` deleted "
                "and nothing else changed, and it collapsed back to the same "
                "magnified grass `close-up` gave in round 1. Every cell here "
                "carries an explicit distance clause, and the wildflowers are "
                "dropped because they supplied depth and littered the near "
                "foreground at the same time." % cell_why,
        },
        overrides={
            "seed": seed,
            "payload:prompt.txt": prompt,
            "key:priority": 40,
        },
        retoken=[(PARENT_DIRTOK, dirtok)],
        by="pipeline/derive_sapling_field_r3_0821.py",
    )

    child["steps"].insert(0, stage_step(dirtok))
    child["bar"] = BAR.replace("TEN PLATES", "EIGHT PLATES").replace(
        "nine siblings", "seven siblings")
    child["the_one_variable"] = (
        "THE SCENE-AND-LIGHTING CLAUSE (%r), and every value of it names "
        "something in the distance. 'wide shot, low angle' is still p09's byte "
        "for byte and still frozen; so are the quality prefix, `no humans`, "
        "the negative, the checkpoint, the size, the steps, the cfg, the "
        "nocontrol arm and its 0.45 scale." % scene)
    child["this_cell"] = cell_why
    child["the_finding_that_bought_this_round"] = (
        "r02 IS THE WHOLE ARGUMENT. It is r01 -- the cell that reproduced "
        "round 1's only pass -- with the four words `wildflowers in the "
        "distance` removed and nothing else touched. r01 holds a ground plane, "
        "a horizon and a treeline; r02 is magnified grass with neither. Same "
        "framing words in both. So the framing word was never the cause in "
        "either round, and p09 passed because a scene clause written for "
        "another reason happened to name something far away."
    )
    child["what_rounds_1_and_2_cost_and_what_they_bought"] = (
        "18 plates, ~54 minutes of otherwise-idle card, $0. Bought: the macro "
        "failure mode is understood and reproducible, the depth cue is "
        "isolated to one clause by a controlled deletion, the seed lottery is "
        "excluded by r01, and two usable plates exist (p09, r01). Round 1's "
        "ten were filed as a breadth batch off a ratified recipe; the cost of "
        "learning this at ten plates instead of two is recorded rather than "
        "argued away."
    )
    child["failure_predicted_in_advance"] = (
        "FIRST: THE TREELINE COMES INTO THE FOREGROUND. `a treeline in the "
        "distance` asks for trees, the negative bans `tree`, and this tree's "
        "negatives have failed to hold position four times. If trees arrive "
        "mid-frame the depth cue has cost the ground plane it bought and t02's "
        "`distant hills` -- which names no bannable object -- is the cell to "
        "carry forward.\n"
        "SECOND: t04's MIST EATS THE CUE. Haze is what makes distant hills "
        "read as distant, but r04 already showed mist collapsing a cell to "
        "silhouettes. If t04 fails where t02 passes, mist is incompatible with "
        "this route and the dataset's cool-light breadth has to come from t06's "
        "overcast instead.\n"
        "THIRD, AND IT IS THE ONE THAT WOULD RE-OPEN THE ROUTE: the ground "
        "plane arrives but sits at the HORIZON, not the lower centre. Then no "
        "wording fixes it and the answer is the crop this batch has already "
        "committed to for scale."
    )
    child["clip77_measured_not_estimated"] = (
        "prompt %d of 77, counted offline on animagine's own vocab before this "
        "file was written; negative inherited at 71 of 77." % n_p)
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
    raise SystemExit(main())
