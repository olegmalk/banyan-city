"""Round 7 -- FOUR cells against the last thin axis a plate round can move.

WHAT IS LEFT. v3 is 44 frames over 17 plates and its own record names three
gaps. LEAF COUNT is one value and no plate round can touch it -- it needs a
tool that draws three, five and six leaves and that tool does not exist. WATER
is closed: four cells over two rounds, one pass that a same-words re-run could
not reproduce. That leaves one: EVERY ONE OF THE SEVENTEEN PLATES IS AN OPEN
LANDSCAPE OR A WOOD. No interior, no built environment, no close ground.

WHY THAT GAP EXISTS, AND WHY IT MAY NOT BE A LAW. Round 2's rule is that what
buys a drawable ground plane is "a LANDFORM or a RECEDING FEATURE -- something
the picture has to be positioned relative to". Rounds 1-6 tested the first half
sixty-odd times and the second half never: every cell any round has asked for
named a hill, a mountain, a ridge, a treeline or a distant field. A COLONNADE,
A WALL RUNNING AWAY FROM CAMERA, A LANE BETWEEN HOUSES is a receding feature
that is not a landform. If the rule is really about RECESSION the built cells
draw a plane; if it is really about landforms they collapse to macro texture
the way ground-cover clauses did in round 1, and the honest conclusion is that
this instrument's dataset is outdoors by construction and the gap is permanent.
Either answer closes an axis that has been open since round 2.

THE LIGHT IS FROZEN AT THE ONE CLAUSE ROUND 6 PROVED. `low sun behind thin
cloud, warm diffuse glow` is w02's, and w02 is the cell that showed warm light
without a season word keeps a green ground where `golden hour` did not. Round 6
also measured what happens when the light goes cool or dim: a snowfield, and a
plate with ZERO green-dominant pixels that step 2 refuses. So the lighting is
not a variable here -- it is the only setting known to be safe, held still so
that a failure is attributable to the scene.

WHY FOUR AND NOT TWELVE, AGAIN. One clause is under test. Round 1 filed ten
cells off a ratified recipe and this lane's own record says a four-cell probe
would have found its failure for 40% of the card time; round 6 was four cells
and answered more than round 5's fourteen did. x04 is the CONTROL.

FILED AT LOW PRIORITY ON PURPOSE. Two iteration-campaign lanes (beats 01-10 and
11-21) are shipping to this same queue tonight and their work outranks a probe.
These four wait behind it; nothing here is a shot, nothing enters a cut, and
DECISIONS.md item 18 ("never train on the output") is open and untouched.

Run:  python3 pipeline/derive_sapling_field_r7_0821.py [--write]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402
from derive_sapling_field_0821 import BAR, assert_under_clip77  # noqa: E402

# The round-4 CONTROL, same parent as rounds 5 and 6.
PARENT = "pipeline/jobs/ep3-sapfld4-u01-0821.yaml"
PARENT_DIRTOK = "sapfld4-u01-0821"

QUALITY = "masterpiece, best quality, very aesthetic, no humans"
FRAMING = "wide shot"   # `low angle` stays DROPPED. Round 4 is why.
# FROZEN, and it is w02's: the one lighting clause round 6 proved keeps a green
# ground. Warm, and it names no season, no temperature and no time of year.
LIGHT = "low sun behind thin cloud, warm diffuse glow"

# THE PRIORITY IS DELIBERATELY WORSE THAN THE QUEUE DEFAULT. box_runner sorts
# ready/ by (priority, name) ASCENDING -- lower runs first (box_runner.py:555)
# -- and box_enqueue defaults an unset priority to 100. The beat campaign files
# ship work at 15; round 6's own plates went at 41 and its inpaints at 55. This
# probe sits at 120, BEHIND EVEN AN UNMARKED JOB, so anything either campaign
# lane files tonight preempts it without having to know this lane exists.
PRIORITY = 120

# (tag, seed, scene clause, which question this cell is)
VARIANTS = [
    ("x01", 20260981, "in a grassy courtyard, a long stone colonnade receding",
     "THE STRONGEST FORM OF THE QUESTION. A colonnade is pure recession and "
     "nothing else -- repeated verticals marching away from camera, no "
     "landform anywhere in the words. `grassy courtyard` comes FIRST so the "
     "near ground is named before the architecture, which is the word order "
     "round 5 used on the water cells (and which did not save them; that is "
     "recorded, not hidden). If any cell draws a plane on recession alone it "
     "is this one."),
    ("x02", 20260982, "beside a low stone wall running into the distance, "
     "green field",
     "THE MINIMAL BUILT FEATURE. One object, no interior, no enclosure -- a "
     "wall is a line in perspective and little else, so this cell separates "
     "RECESSION from ENCLOSURE. If x01 fails and x02 passes, what the "
     "checkpoint needs is a perspective line rather than a place; if both "
     "fail, recession without a landform draws nothing and the axis closes."),
    ("x03", 20260983, "on a cobbled lane between old stone houses, grass "
     "verges",
     "THE ONE THAT SHOULD BE HARDEST AND IS WORTH THE MOST. Two failure modes "
     "at once: the ground is named COBBLES, which is grey, and grey is what "
     "starved w01 to zero green-dominant pixels; and a village lane is the "
     "strongest figure prime this tree has ever been asked for. `grass verges` "
     "is the rootable strip and it is the whole hope of the cell. It is filed "
     "anyway because r08 -- `on a dirt path, green field` -- is one of the "
     "best ground planes in the entire set, and a lane is that plate with "
     "buildings instead of trees."),
    ("x04", 20260984, "in a green meadow, distant hills",
     "THE CONTROL, AND IT IS w02'S EXACT WORDS AT A NEW SEED. Round 6 turned "
     "on w02 -- warm light with the season word deleted returning a green "
     "plane where `golden hour` returned tan macro grass -- and w02 is one "
     "picture. This re-runs it. If x04 comes back tan or plane-less, w02 was "
     "seed luck, round 6's warm-light finding is unsupported, and the other "
     "three cells cannot be read at all. READ THIS ONE FIRST."),
]

CONSUMER = (
    "THE LAST THIN AXIS IN pipeline/lora/manifest-sapling.yaml THAT A PLATE "
    "ROUND CAN MOVE. v3 is 44 frames over 17 plates and every one of those "
    "plates is an open landscape or a wood -- its own record says so, and says "
    "why: the recipe that buys a drawable plane is a distant-landform clause "
    "and a landform is outdoors by construction. This tests whether that is "
    "the recipe or just the habit. What eats a passing plate is step 2 "
    "(pipeline/beat16_sapling_composite.py) and step 3 "
    "(pipeline/derive_sapling_lora_naturalize_0821.py). A FAILING BATCH IS "
    "ALSO A RESULT AND IS WORTH THE CARD TIME: four cells that all collapse "
    "close an axis that has been open since round 2 and stop a later round "
    "paying for it again. No cut, no beat, no promotion, $0 on the card, "
    "filed at priority %d so the beat campaign runs first, and DECISIONS.md "
    "item 18 is open and is not touched by building the set the question is "
    "about." % PRIORITY)


def build(tag, seed, scene, cell_why):
    new_id = "ep3-sapfld7-%s-0821" % tag
    dirtok = "sapfld7-%s-0821" % tag
    prompt = "%s, %s, %s, %s" % (QUALITY, scene, LIGHT, FRAMING)
    n_p = assert_under_clip77("%s prompt" % new_id, prompt)

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "sapling-dataset lane, 2026-08-21 round 7 (the built-scene probe)",
            "consumer": CONSUMER,
            "success":
                "One 832x1216 png at seed %d, cel dialect, of '%s' under '%s' "
                "at 'wide shot': STRAIGHT horizon, a clean drawable ground "
                "plane in the lower centre with NO built structure standing in "
                "it, no plant, NO FIGURE, and a GREEN-DOMINANT region in the "
                "lower half. Three of these four cells name stone, and stone "
                "is grey: w01 came back grey and the palette sampler found "
                "ZERO green-dominant pixels in its whole lower half and "
                "refused the plate. A beautiful courtyard with a paved floor "
                "has failed."
                % (seed, scene, LIGHT),
            "why":
                "%s\n\nTHE RECIPE IS NOT UNDER TEST AND NEITHER IS THE LIGHT. "
                "Rounds 1-4 settled the recipe, round 5 spent it and round 6 "
                "found the one lighting clause that keeps a green ground: the "
                "quality prefix, `no humans`, `wide shot` with NO `low angle`, "
                "the negative, the checkpoint, the size, the steps, the cfg, "
                "the staging and the nocontrol arm at 0.45 are inherited byte "
                "for byte from the round-4 control, and the lighting is frozen "
                "at %r, which is w02's. THE ONE VARIABLE IS THE SCENE CLAUSE, "
                "and every value names a RECEDING FEATURE THAT IS NOT A "
                "LANDFORM." % (cell_why, LIGHT),
        },
        overrides={
            "seed": seed,
            "payload:prompt.txt": prompt,
            "key:priority": PRIORITY,
        },
        retoken=[(PARENT_DIRTOK, dirtok)],
        by="pipeline/derive_sapling_field_r7_0821.py",
    )

    child["bar"] = BAR.replace("TEN PLATES", "FOUR PLATES")
    child["the_one_variable"] = (
        "THE SCENE CLAUSE (%r). The lighting is frozen at %r and the framing "
        "at %r; everything else is the round-4 control's."
        % (scene, LIGHT, FRAMING))
    child["this_cell"] = cell_why
    child["the_rule_this_batch_tests"] = (
        "ROUND 2 SAID A LANDFORM **OR A RECEDING FEATURE** BUYS A DRAWABLE "
        "GROUND PLANE, AND ONLY THE FIRST HALF HAS EVER BEEN TESTED. Every "
        "cell of rounds 1-6 named a hill, a mountain, a ridge, a treeline or a "
        "distant field. These four name recession with NO landform in it -- a "
        "colonnade, a wall in perspective, a lane between houses -- and one "
        "control that names the landform. Falsifiable in one batch: if all "
        "three built cells come back as macro texture the way round 1's "
        "ground-cover clauses did, then recession is not the mechanism, "
        "landforms are, and this dataset is outdoors permanently.")
    child["why_four_cells"] = (
        "A PROBE, not a breadth batch, and the second one in a row. Round 1 "
        "filed ten cells off a ratified recipe and "
        "review/ep3-sapling-dataset-0821/plates-0821.yaml records in this "
        "lane's own words that a four-cell probe would have found its failure "
        "for 40% of the card time. Round 6 was four cells and answered more "
        "than round 5's fourteen. x04 is the CONTROL so a batch-wide failure "
        "can be told apart from the rule being wrong.")
    child["failure_predicted_in_advance"] = (
        "FIRST, AND IT IS THE ONE THIS TREE HAS THE WORST RECORD ON: A FIGURE. "
        "The negatives here have failed to hold position five times, and the "
        "only reason rounds 5 and 6 went 22 for 22 clean is that they asked "
        "for EMPTY LANDSCAPES, where there is nobody for the checkpoint to "
        "put in. A courtyard and a village lane are places people live, and "
        "this is the hardest that ban has ever been pushed. A plate with a "
        "figure in it is DELETED under D3, not cropped -- so a batch that "
        "comes back populated costs its whole card time and returns the "
        "finding that built scenes are unreachable for this lane at this "
        "negative, which is worth knowing and is not worth a sixth attempt at "
        "rewording the ban.\n"
        "SECOND: THE STONE IS GREY AND GREY STARVES THE PALETTE. w01 was "
        "refused at step 2 with ZERO green-dominant pixels in its whole lower "
        "half. A courtyard floored in flagstones or a lane floored in cobbles "
        "is the same refusal arriving through a MATERIAL word instead of a "
        "lighting one. Every cell names grass, lawn or verges first for "
        "exactly this reason, and round 5 proved that putting the green word "
        "first did not save the water cells.\n"
        "THIRD: THE BUILDING STANDS IN THE ROOTABLE STRIP. Round 3 "
        "pre-registered this shape for treelines and it did not happen; round "
        "5 pre-registered it for water and it happened 3 of 3. A wall or a "
        "house wall crossing the lower centre is a STRUCTURE, and D2 rejects a "
        "plate whose plane has one in it because the 0.30 pass preserves what "
        "it finds in the init.\n"
        "FOURTH, AND IT INVALIDATES THE BATCH RATHER THAN ANSWERING IT: x04, "
        "the control, fails. w02's words at a new seed producing tan grass or "
        "no plane would mean round 6's warm-light finding rests on one "
        "picture. Read x04 first.")
    child["clip77_measured_not_estimated"] = (
        "prompt %d of 77, counted offline on animagine's own vocab before this "
        "file was written; negative inherited from the round-4 control at 71 "
        "of 77." % n_p)
    child["priority_is_deliberate"] = (
        "%d, and box_runner sorts ready/ by (priority, name) ASCENDING, so a "
        "LOWER number runs first and an unset priority defaults to 100. This "
        "is therefore behind even an unmarked job. Two iteration-campaign "
        "lanes (beats 01-10 and 11-21) are filing ship work to this same card "
        "tonight -- at 15 -- and a variety probe does not preempt ship work. "
        "This lane also does NOT refill after these four: the campaign owns "
        "the card." % PRIORITY)
    return new_id, child


def main():
    write = "--write" in sys.argv
    out = []
    for tag, seed, scene, cell_why in VARIANTS:
        new_id, child = build(tag, seed, scene, cell_why)
        path = "pipeline/jobs/%s.yaml" % new_id
        if write:
            out.append(derive_spec.write(child, path))
            print("wrote %s  seed=%d  prio=%d  %s"
                  % (path, seed, PRIORITY, scene))
        else:
            print("would write %s  seed=%d  prio=%d  %s"
                  % (path, seed, PRIORITY, scene))
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
