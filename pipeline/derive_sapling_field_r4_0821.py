"""Round 4 -- `low angle` was cargo from p09 and it is buying a fisheye.

ROUND 3 FIXED THE GROUND PLANE AND EXPOSED THE NEXT DEFECT. Every cell that
named a distant landform came back with a horizon and a rootable plane, which
is the round-3 hypothesis confirmed: t02 (distant hills), t04 (hills in mist)
and t07 (dry grass + hills) are clean, and nothing returned the macro grass
that took six of round 1.

But six of the eight are BARREL-DISTORTED -- t01, t04, t05, t06, t08 curve the
horizon like an ultra-wide lens, t01 arches its treeline right over the top of
the frame, and t05's path narrows to a wedge. A curved horizon is not a ground
plane a cel seedling can be drawn onto standing straight up: the composite
draws a vertical stem with a measured root point, and the plate's own geometry
has to agree with it.

THE CAUSE IS `low angle`, AND IT IS CARGO I CARRIED WITHOUT WARRANT. It came
from p09 and was frozen through rounds 2 and 3 on the reading that the framing
clause was load-bearing. r02 killed that reading -- the DISTANCE clause is the
lever -- and I froze the framing anyway instead of retiring the half of it that
no longer had an argument. `wide shot` earns its place; `low angle` was never
tested on its own and is what a diffusion model draws as a fisheye.

So round 4 drops `low angle` and keeps `wide shot` plus the distance clause,
across the scene and lighting values round 3 proved readable. If the curvature
goes and the plane stays, the recipe is settled and the rest of the gate is
breadth. If the plane goes with it, `low angle` was buying both and the answer
is a crop of a round-3 plate, which is where the scale axis already lives.

Run:  python3 pipeline/derive_sapling_field_r4_0821.py [--write]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402
from derive_sapling_field_0821 import (BAR, assert_under_clip77,  # noqa: E402
                                       stage_step)

PARENT = "pipeline/jobs/ep3-sapfld3-t02-0821.yaml"
PARENT_DIRTOK = "sapfld3-t02-0821"

QUALITY = "masterpiece, best quality, very aesthetic, no humans"
FRAMING = "wide shot"   # `low angle` DROPPED -- it was buying the fisheye

# Every cell names something FAR AWAY. That is the variable r02 isolated.
VARIANTS = [
    ("u01", 20260941, "in a green meadow, distant hills, clear sky, day",
     "THE CONTROL. t02 -- round 3's cleanest cell -- with `low angle` removed "
     "and nothing else touched. This one cell answers whether the curvature "
     "was the framing word."),
    ("u02", 20260942, "in a green meadow, distant hills, sunset, orange sky",
     "The warm cell, on a scene that held its plane in round 3. t03's sunset "
     "failed on a black silhouetted foreground; distant hills instead of a "
     "treeline should keep the near ground lit."),
    ("u03", 20260943, "in a green meadow, distant hills, morning, mist",
     "t04 without the fisheye. t04 already passed on its plane, so if this "
     "loses it, `low angle` was buying the plane too and that is the finding."),
    ("u04", 20260944, "in a green meadow, distant hills, overcast, soft light",
     "The flat cell, re-run: t06's overcast failed on distortion and darkness "
     "at a treeline, so the light is still unjudged on a readable plate."),
    ("u05", 20260945, "in a field of dry grass, distant hills, autumn, clear sky",
     "t07 without the fisheye -- the palette cell. The composite samples its "
     "greens FROM THE PLATE, so this is the test of whether a green sapling "
     "can be lit into a dry field or comes out straw."),
    ("u06", 20260946, "on a grassy hillside, distant mountains, clear sky, day",
     "The r05 terrain, which passed in round 2 on the strength of a landform "
     "the model supplied unprompted, now with the landform named."),
    ("u07", 20260947, "in a green meadow, a treeline in the distance, clear sky, day",
     "t01's cell without `low angle`. t01 arched its trees over the frame; if "
     "they sit down on the horizon here, treelines are usable and the dataset "
     "gains a second depth vocabulary alongside hills."),
    ("u08", 20260948, "in a green field, a dirt path receding into the distance, day",
     "t05 without the fisheye. A path is the only cell that hands the "
     "composite an unvegetated strip to root in, which is worth one more try "
     "at a framing that does not narrow it to a wedge."),
]


def build(tag, seed, scene, cell_why):
    new_id = "ep3-sapfld4-%s-0821" % tag
    dirtok = "sapfld4-%s-0821" % tag
    prompt = "%s, %s, %s" % (QUALITY, scene, FRAMING)
    n_p = assert_under_clip77("%s prompt" % new_id, prompt)

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "sapling-dataset lane, 2026-08-21 round 3",
            "consumer":
                "beat16_sapling_composite.py, which draws a VERTICAL stem at a "
                "measured root point and therefore needs a plate whose horizon "
                "is straight. Round 3 bought the ground plane and bent it; "
                "these plates are the same planes without the curve, and they "
                "are what step 2 of the sapling dataset actually consumes. No "
                "cut, no beat, no promotion.",
            "success":
                "One 832x1216 png at seed %d, cel dialect, of %s at 'wide "
                "shot', with a STRAIGHT horizon and a clean drawable ground "
                "plane in the lower centre, no plant and no figure. A curved "
                "horizon is a FAIL here even where round 3 let it pass. Judged "
                "by eye at 1:1 with its seven siblings."
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
            "key:priority": 41,
        },
        retoken=[(PARENT_DIRTOK, dirtok)],
        by="pipeline/derive_sapling_field_r4_0821.py",
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
        "ROUND 3 CONFIRMED ITS HYPOTHESIS AND EXPOSED THE NEXT DEFECT. Every "
        "cell naming a distant landform returned a horizon and a rootable "
        "plane -- t02, t04 and t07 clean, and not one macro-grass frame in "
        "eight, against six of ten in round 1. But six of the eight are "
        "BARREL-DISTORTED: t01 arches its treeline over the top of the frame, "
        "t05 narrows its path to a wedge, and t02/t04/t06/t08 curve the "
        "horizon. A curved horizon is not a plane a cel seedling can stand "
        "up on -- beat16_sapling_composite.py draws a VERTICAL stem at a "
        "measured root point and the plate's geometry has to agree with it.")
    child["the_cargo_i_carried_without_warrant"] = (
        "`low angle` came from p09 and was frozen through rounds 2 and 3 on "
        "the reading that the framing clause was load-bearing. r02 KILLED "
        "THAT READING -- the distance clause is the lever -- and I froze the "
        "framing anyway instead of retiring the half of it that no longer had "
        "an argument. `wide shot` earns its place; `low angle` was never "
        "tested alone and is what this checkpoint draws as a fisheye. Two "
        "rounds of curvature is what carrying it cost.")
    child["what_rounds_1_to_3_cost_and_what_they_bought"] = (
        "26 plates, ~78 minutes of otherwise-idle card, $0, and 8 usable "
        "ground planes. Bought one mechanism per round, each by a controlled "
        "change: round 1 that a ground-cover noun returns a macro of itself, "
        "round 2 (by DELETING four words from the cell that passed) that a "
        "named distant feature and not the framing word is what buys depth, "
        "round 3 that the depth cue generalises across scenes and lighting. "
        "Two of my three round-opening predictions were wrong and both are "
        "kept above their results.")
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
