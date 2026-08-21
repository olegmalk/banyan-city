"""Round 5 -- the recipe is SETTLED; this round spends it on VARIETY.

WHAT ROUNDS 1-4 SETTLED, AND WHY THIS ROUND CHANGES NOTHING ABOUT IT.
Round 1: a scene clause naming only GROUND COVER returns a macro of that ground
cover, at any framing. Round 2: the lever is the DISTANCE CLAUSE, proved by
DELETING four words from the one cell that passed and watching it collapse.
Round 3: the depth cue generalises across scene and lighting -- and bends the
horizon. Round 4: `low angle` was the fisheye, and dropping it took the batch to
8 of 8. Every cell below carries the round-4 recipe byte for byte -- the quality
prefix, `no humans`, `wide shot` with NO `low angle`, the negative, the
checkpoint, the size, the steps, the cfg, the nocontrol arm and its 0.45 scale.
THE ONE VARIABLE IS THE SCENE-AND-LIGHTING CLAUSE, and it always names something
far away.

WHY A ROUND 5 AT ALL: THE DATASET'S OWN MANIFEST NAMES ITS CAP.
pipeline/lora/manifest-sapling.yaml is 26 frames over ELEVEN distinct scenes,
and pipeline/lora/README.md gates the set on VARIETY, not count. Read the eleven
lightings the v1 plates actually carry: flat daylight, sunset backlight, dawn
mist, heavy overcast, alpine midday, forest dapple, even daylight, pale dawn,
strong backlight, hard midday sun, bright daylight. Every one of them is DAY.
There is no dusk, no night, no storm, no rain, no golden hour, no winter light
and no water anywhere in the set -- so a LoRA trained on it learns `bnysapling`
with a daylit green field baked into the trigger, which is the exact failure the
plates file was written to prevent one axis over (a shared backdrop entering the
trigger). Fourteen cells here, all new scene/lighting combinations, none of them
a repeat of a v1 plate.

WHAT IS DELIBERATELY NOT VARIED: THE GREEN. u05 (dry tan plain) rendered fine as
a picture and was DROPPED from v1 because beat16_sapling_composite.py samples the
plant's palette from the plate's own greens and that plate had no green-dominant
pixel in its whole lower half -- it crashed the tool, which is now a refusal with
a reason. So every cell below keeps a green ground plane in the words, and the
lighting is what moves. The two cells that put that at risk (night/moonlight,
storm dark) are pre-registered below as the ones most likely to come back
green-starved, and D5 is what deletes them if they do.

Run:  python3 pipeline/derive_sapling_field_r5_0821.py [--write]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402
from derive_sapling_field_0821 import BAR, assert_under_clip77  # noqa: E402

# The round-4 CONTROL -- the cell that isolated `low angle` and came back with a
# straight horizon. Its steps, negative, size, checkpoint and arms are the
# settled recipe and are inherited untouched, including its own staging steps.
PARENT = "pipeline/jobs/ep3-sapfld4-u01-0821.yaml"
PARENT_DIRTOK = "sapfld4-u01-0821"

QUALITY = "masterpiece, best quality, very aesthetic, no humans"
FRAMING = "wide shot"   # `low angle` stays DROPPED. Round 4 is why.

# Every cell: (tag, seed, scene, why this cell). Every scene names something FAR
# AWAY (the round-2 lever), keeps a GREEN ground (the D5 palette law), and pairs
# it with a lighting or a landform the v1 manifest does not have.
VARIANTS = [
    ("v01", 20260951, "in a green meadow, distant hills, dusk, deep blue twilight sky",
     "DUSK. v1's coolest light is dawn mist; nothing in the set is after the "
     "sun. Same scene words as the u01 control so the lighting is the only "
     "thing that moved off a plate already known to work."),
    ("v02", 20260952, "in a green meadow, distant hills, night, moonlight, blue darkness",
     "NIGHT. The furthest cell from the set's daylit centre and the one most "
     "likely to fail D5 -- if the greens go to blue-grey the composite has no "
     "palette to sample and the frame is deleted, not curated."),
    ("v03", 20260953, "in a green meadow, distant hills, storm clouds, dark sky, a shaft of light",
     "STORM LIGHT. Directional by construction, which is D4's whole clause: a "
     "break in cloud gives the composite a luminance gradient to carry into "
     "the plant instead of the flat overcast v1 already has at u04."),
    ("v04", 20260954, "in a green meadow, distant hills, golden hour, long shadows, warm side light",
     "GOLDEN HOUR, and it is NOT u02's sunset. u02 is warm BACKLIGHT with an "
     "orange sky behind the subject; this is low warm light from the SIDE with "
     "cast shadows on the plane -- a different gradient for D4 to measure."),
    ("v05", 20260955, "in a green field, distant hills, rain, wet ground, grey sky",
     "RAIN. Wet ground is a new plane texture as well as a new light, and the "
     "set has no weather in it at all."),
    ("v06", 20260956, "beside a lake, green banks, distant mountains, calm water, day",
     "WATER, which the set has none of. Banks are the rootable strip, the far "
     "shore is the distance clause, and r06 (creek) proved in round 2 that a "
     "banked waterway holds its plane."),
    ("v07", 20260957, "beside a shallow creek, green banks, distant hills, early morning light",
     "r06's exact scene, which PASSED in round 2 and then never made it into "
     "v1 because step 2 ran on the eleven plates and this was not one of them. "
     "Cheapest breadth in the batch: a known-good cell the dataset lacks."),
    ("v08", 20260958, "on a green clifftop, the sea far below, distant horizon, day",
     "COASTAL. The distance cue is a sea horizon rather than a landform, which "
     "is a third depth vocabulary after hills and treelines -- and a clifftop "
     "puts the rootable plane in the near field by construction."),
    ("v09", 20260959, "on a green ridge, a distant valley, low fog below, morning",
     "FOG BELOW, not fog around. u03's valley mist sits IN the scene and r04 "
     "showed mist collapsing a cell to silhouettes; here the haze is beneath "
     "the camera and the near plane stays lit."),
    ("v10", 20260960, "in a green meadow, distant snow peaks, cold clear winter light",
     "WINTER LIGHT ON A GREEN PLANE. u06 has snow-capped mountains under "
     "BRIGHT MIDDAY; this asks for the cold low-contrast light itself while "
     "keeping the ground green, which is the D5 constraint doing the steering."),
    ("v11", 20260961, "on a green riverbank, a wide river receding into the distance, evening",
     "A RECEDING FEATURE THAT IS NOT A PATH. u08's dirt path returned a forest "
     "avenue; a river recedes the same way and names no bannable object, so it "
     "tests the depth cue without asking the negative to hold `tree` again."),
    ("v12", 20260962, "in a green meadow, distant hills, after rain, puddles, breaking clouds",
     "POST-RAIN. Puddles are specular and the set is entirely matte; breaking "
     "cloud is the strongest directional light available without a sunset."),
    ("v13", 20260963, "in a green meadow, distant hills, hazy heat, pale white sky, afternoon",
     "HEAT HAZE. A high-key, low-saturation cell -- the opposite end of the "
     "exposure axis from v02 and v03, and the set has nothing washed out."),
    ("v14", 20260964, "in a green valley, distant snow mountains, alpenglow, pink light on the peaks",
     "ALPENGLOW. Warm distance against a cool near plane, which is the one "
     "colour-temperature SPLIT in the batch; every v1 frame is lit by a single "
     "temperature top to bottom."),
]

CONSUMER = (
    "V2 CURATION of the sapling LoRA dataset. v1 is "
    "pipeline/lora/manifest-sapling.yaml -- 26 frames, 11 scenes, and by its "
    "own gate (pipeline/lora/README.md: variety, not count) it is capped on "
    "lighting: all eleven plates are DAYLIT. These plates are the missing "
    "half of that axis, and what eats them is step 2 "
    "(beat16_sapling_composite.py, which draws a vertical stem at a measured "
    "root point and samples its greens from the plate) and then step 3 (the "
    "0.30 inpaint, pipeline/derive_sapling_lora_naturalize_0821.py). NOTHING "
    "here is a shot: no cut, no beat, no promotion, and DECISIONS.md item 18 "
    "('never train on the output') is still open and is not touched by "
    "building the set the question is about.")


def build(tag, seed, scene, cell_why):
    new_id = "ep3-sapfld5-%s-0821" % tag
    dirtok = "sapfld5-%s-0821" % tag
    prompt = "%s, %s, %s" % (QUALITY, scene, FRAMING)
    n_p = assert_under_clip77("%s prompt" % new_id, prompt)

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "sapling-dataset lane, 2026-08-21 round 5 (v2 variety)",
            "consumer": CONSUMER,
            "success":
                "One 832x1216 png at seed %d, cel dialect, of %s at 'wide "
                "shot': STRAIGHT horizon, clean drawable ground plane in the "
                "lower centre, no plant, no figure, AND a green-dominant "
                "region in the lower half for the composite to sample its "
                "palette from. The lighting must be READABLE as the named one "
                "-- a cell that comes back as generic daylight has failed even "
                "with a perfect plane, because the light is the only thing "
                "this round is buying. Judged by eye at 1:1 against the v1 "
                "contact sheet, not against its own siblings."
                % (seed, scene),
            "why":
                "%s\n\nTHE RECIPE IS NOT UNDER TEST HERE. Rounds 1-4 settled "
                "it: a ground-cover noun alone returns a macro of itself "
                "(round 1); a named DISTANT feature and not the framing word "
                "is what buys depth (round 2, proved by deleting four words "
                "from the only passing cell); the cue generalises across "
                "scenes (round 3); `low angle` was cargo and was drawing the "
                "fisheye (round 4, 8 of 8 after dropping it). This round "
                "spends that recipe on the axis v1's own manifest is thinnest "
                "on -- every one of its eleven plates is lit by DAY." % cell_why,
        },
        overrides={
            "seed": seed,
            "payload:prompt.txt": prompt,
        },
        retoken=[(PARENT_DIRTOK, dirtok)],
        by="pipeline/derive_sapling_field_r5_0821.py",
    )

    child["bar"] = BAR.replace("TEN PLATES", "FOURTEEN PLATES")
    child["the_one_variable"] = (
        "THE SCENE-AND-LIGHTING CLAUSE (%r). Every value names something in "
        "the distance (round 2's lever) and keeps a green ground plane (D5, "
        "which is what dropped u05 from v1). `wide shot` with NO `low angle` "
        "is round 4's settled framing and is frozen; so are the quality "
        "prefix, `no humans`, the negative, the checkpoint, the size, the "
        "steps, the cfg, the staging steps, the nocontrol arm and its 0.45 "
        "scale." % scene)
    child["this_cell"] = cell_why
    child["what_the_v1_manifest_says_it_is_missing"] = (
        "26 frames, 11 distinct scenes, scale tiers l=7 m=8 s=6 xl=5, and "
        "leaf_count_values: 1 -- the manifest names two caps out loud. The "
        "leaf-count cap needs a tool that can draw three, five and six leaves "
        "and that tool does not exist, so it is NOT what this round attacks. "
        "The other cap is legible in the captions rather than in a field: the "
        "lighting values are flat daylight, sunset backlight, dawn mist, heavy "
        "overcast, alpine midday, forest dapple, even daylight, pale dawn, "
        "strong backlight, hard midday sun and bright daylight. All eleven are "
        "DAY. A subject LoRA whose every frame shares a time of day learns the "
        "time of day into the trigger, which is the same defect as the shared "
        "backdrop the plates file was written to kill.")
    child["failure_predicted_in_advance"] = (
        "FIRST, AND IT IS THE ONE I EXPECT: THE DARK CELLS COME BACK "
        "GREEN-STARVED. v02 (night) and v03 (storm) are asking for a plate "
        "whose greens survive a blue or near-black key. u05 already proved the "
        "consequence -- no green-dominant pixel in the lower half and "
        "beat16_sapling_composite REFUSES the plate -- so if these two fail "
        "they fail at step 2, not at the eye, and the dataset's dark end has "
        "to come from v01/v12 (dusk, breaking cloud) instead of true night.\n"
        "SECOND: THE WATER CELLS PUT THE PLANE IN THE WRONG PLACE. v06, v07 "
        "and v11 all hand the frame a horizontal band of water; if it lands in "
        "the lower centre it has eaten the rootable strip and the cue that "
        "bought depth has cost the plane -- the same failure shape round 3 "
        "pre-registered for treelines. r06 passed in round 2 with banks in the "
        "near field, which is why the words say `green banks` first.\n"
        "THIRD: THE LIGHT IS NAMED AND NOT DRAWN. `golden hour`, `alpenglow` "
        "and `hazy heat` are painter's words, not objects; this checkpoint may "
        "return the same clear-day plate for all three. That is a real result "
        "and it is scored as one -- the cells are cheap, and a lighting word "
        "that does nothing is worth knowing before v2 curation counts on it.")
    child["clip77_measured_not_estimated"] = (
        "prompt %d of 77, counted offline on animagine's own vocab before this "
        "file was written; negative inherited from the round-4 control at 71 "
        "of 77. Ten specs died rc=9 on box_preflight's clip77 guard on "
        "2026-08-21 with the card idle, which is why this is a hard refusal in "
        "the deriver and not a check at the queue." % n_p)
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
