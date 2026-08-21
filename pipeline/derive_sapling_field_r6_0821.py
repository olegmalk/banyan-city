"""Round 6 -- FOUR cells, and each one DELETES one word from a round-5 failure.

THE RULE UNDER TEST, AND ROUND 5 IS WHERE IT CAME FROM. Round 5 asked fourteen
plates for non-daylit light and four came back usable. Reading the ten that did
not, the failures sort into one shape:

  v10 `cold clear WINTER light` + `distant SNOW peaks` -> a snowfield, no green
  v14 `ALPENGLOW`, `pink light on the PEAKS`           -> snow and conifers
  v04 `GOLDEN HOUR, long shadows`                      -> tan macro grass
  v13 `HAZY HEAT, pale white sky`                      -> an airbrush painting

and the two strongest passes sort into the other:

  v02 `night, MOONLIGHT, blue darkness`                -> the greenest plate of 14
  v03 `STORM CLOUDS, dark sky, a shaft of light`       -> a clean flat green plane

A LIGHTING WORD THAT NAMES A SEASON, A TEMPERATURE OR A TIME OF YEAR CARRIES ITS
OWN GROUND MATERIAL INTO THE FRAME. A LIGHTING WORD THAT NAMES ONLY A STATE OF
THE SKY DOES NOT -- darkness and cloud have no material to put on the ground.
Round 5 filed that as "a lighting word on this checkpoint carries a whole
scene", which is true and is not yet actionable. This round makes it actionable
or kills it, and it does so the way round 2 did: by DELETING the suspect words
from a cell that failed and changing nothing else.

WHY FOUR AND NOT FOURTEEN. Round 1 filed ten cells on the argument that only the
words varied and a four-cell probe would have found its failure for 40% of the
card time; that cost is recorded in plates-0821.yaml in this lane's own words.
The recipe is not what is under test here -- one clause is -- so this is a probe
and it is sized like one.

THE CONSUMER IS A NUMBER IN THE MANIFEST I JUST WROTE. v2 is 37 frames over 15
plates and its own record says the daylit half still outnumbers the new one
TWENTY-SIX TO ELEVEN. Four more non-daylit plates is the cheapest thing that
moves that ratio, and if the rule holds it also says which lighting words are
worth asking for at all. Nothing here is a shot, nothing enters a cut, and
DECISIONS.md item 18 ("never train on the output") is open and untouched.

Run:  python3 pipeline/derive_sapling_field_r6_0821.py [--write]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402
from derive_sapling_field_0821 import BAR, assert_under_clip77  # noqa: E402

# The round-4 CONTROL, same parent as round 5. Straight horizon, settled recipe.
PARENT = "pipeline/jobs/ep3-sapfld4-u01-0821.yaml"
PARENT_DIRTOK = "sapfld4-u01-0821"

QUALITY = "masterpiece, best quality, very aesthetic, no humans"
FRAMING = "wide shot"   # `low angle` stays DROPPED. Round 4 is why.
GROUND = "in a green meadow, distant hills"   # frozen: round 2's depth lever,
                                              # and it names no material.

# (tag, seed, lighting clause, which round-5 failure this deletes)
VARIANTS = [
    ("w01", 20260971, "overcast at dusk, the last grey light, no sun",
     "DELETES `deep blue twilight sky` FROM v01. v01 is the round-5 result "
     "that hurts most: it passed the eye and REFUSED at the palette sampler "
     "with ONE green-dominant pixel at RGB (2,7,2), because a blue key leaves "
     "no green to sample. Same time of day, grey key instead of blue. If this "
     "comes back green-dominant the dark end of the dataset gains dusk; if it "
     "comes back blue again the finding is that the checkpoint's dusk IS blue "
     "and dusk is closed for this instrument."),
    ("w02", 20260972, "low sun behind thin cloud, warm diffuse glow",
     "DELETES `golden hour` AND `long shadows` FROM v04, keeping the warm low "
     "light they were asking for. v04 returned magnified tan grass with no "
     "ground plane at all -- the season word brought dry grass with it. This "
     "asks for the same photons and names no time of year."),
    ("w03", 20260973, "moonlight through broken cloud, patches of shadow",
     "EXTENDS v02, THE ONE CONFIRMED WINNER, and is the control of this batch. "
     "v02 (`night, moonlight, blue darkness`) is the greenest plate of the "
     "fourteen, so moonlight demonstrably does not starve the palette; "
     "`broken cloud` adds the directional patchiness D4 measures. If w03 "
     "fails while v02 passed, the variable is the seed and not the words, and "
     "that is worth knowing before any of the other three are read."),
    ("w04", 20260974, "cold clear air, pale blue light, long shadows",
     "DELETES `winter` AND `snow peaks` FROM v10, keeping the cold light. v10 "
     "asked for `cold clear winter light` over `distant snow peaks` and "
     "returned a SNOWFIELD -- the ground word lost to the season word. Nothing "
     "here names a season or a frozen material, and `distant hills` is the "
     "depth cue instead of peaks."),
]

CONSUMER = (
    "THE 26:11 RATIO IN pipeline/lora/manifest-sapling.yaml. v2 is 37 frames "
    "over 15 plates and the lighting axis it just opened is four plates wide "
    "against eleven daylit ones -- its own record says so. Four more non-daylit "
    "plates is the cheapest thing that moves it, and the cells are chosen so "
    "that the ANSWER is worth as much as the pictures: each one deletes the "
    "word round 5 measured as carrying a ground material, from the cell it "
    "carried it into. What eats a passing plate is step 2 "
    "(pipeline/beat16_sapling_composite.py) and step 3 "
    "(pipeline/derive_sapling_lora_naturalize_0821.py). No cut, no beat, no "
    "promotion, $0 on an otherwise-idle card, and DECISIONS.md item 18 is open "
    "and is not touched by building the set the question is about.")


def build(tag, seed, lighting, cell_why):
    new_id = "ep3-sapfld6-%s-0821" % tag
    dirtok = "sapfld6-%s-0821" % tag
    prompt = "%s, %s, %s, %s" % (QUALITY, GROUND, lighting, FRAMING)
    n_p = assert_under_clip77("%s prompt" % new_id, prompt)

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "sapling-dataset lane, 2026-08-21 round 6 (the word probe)",
            "consumer": CONSUMER,
            "success":
                "One 832x1216 png at seed %d, cel dialect, of a green meadow "
                "under '%s' at 'wide shot': STRAIGHT horizon, clean drawable "
                "ground plane in the lower centre, no plant, no figure, AND a "
                "GREEN-DOMINANT region in the lower half. The green is the "
                "whole question in three of these four cells -- v10 and v04 "
                "each returned a picture that was fine and had no green in it, "
                "and v01 returned green so blue the palette sampler found one "
                "pixel of it. A cell that comes back as generic daylight has "
                "also failed: the light must be READABLE as the named one."
                % (seed, lighting),
            "why":
                "%s\n\nTHE RECIPE IS NOT UNDER TEST. Rounds 1-4 settled it and "
                "round 5 spent it: the quality prefix, `no humans`, `wide shot` "
                "with NO `low angle`, the negative, the checkpoint, the size, "
                "the steps, the cfg, the staging and the nocontrol arm at 0.45 "
                "are inherited byte for byte from the round-4 control. The "
                "GROUND CLAUSE is frozen too, at `%s` -- round 2's depth lever, "
                "and the one phrasing that names no material. THE ONE VARIABLE "
                "IS THE LIGHTING CLAUSE, and every value is a round-5 clause "
                "with its suspect word removed." % (cell_why, GROUND),
        },
        overrides={
            "seed": seed,
            "payload:prompt.txt": prompt,
        },
        retoken=[(PARENT_DIRTOK, dirtok)],
        by="pipeline/derive_sapling_field_r6_0821.py",
    )

    child["bar"] = BAR.replace("TEN PLATES", "FOUR PLATES")
    child["the_one_variable"] = (
        "THE LIGHTING CLAUSE (%r). The ground clause is frozen at %r and the "
        "framing at %r; everything else is the round-4 control's."
        % (lighting, GROUND, FRAMING))
    child["this_cell"] = cell_why
    child["the_rule_this_batch_tests"] = (
        "A LIGHTING WORD THAT NAMES A SEASON, A TEMPERATURE OR A TIME OF YEAR "
        "CARRIES ITS OWN GROUND MATERIAL INTO THE FRAME; A LIGHTING WORD THAT "
        "NAMES ONLY A STATE OF THE SKY DOES NOT. Evidence it was drawn from, "
        "all round 5: `winter`+`snow peaks` returned a snowfield (v10), "
        "`alpenglow`+`peaks` returned snow and conifers (v14), `golden hour` "
        "returned tan macro grass (v04) and `hazy heat` returned an airbrush "
        "painting (v13) -- while `night, moonlight` (v02) and `storm clouds, "
        "a shaft of light` (v03) each kept a clean green plane and were the two "
        "best plates of the fourteen. Falsifiable in one batch: if w02 and w04 "
        "come back tan and white anyway, the season word was never the carrier "
        "and the rule is wrong.")
    child["why_four_cells"] = (
        "This is a PROBE, not a breadth batch. Round 1 filed ten cells off a "
        "ratified recipe on the argument that only the words varied, and this "
        "lane's own record in review/ep3-sapling-dataset-0821/plates-0821.yaml "
        "says a four-cell probe would have found its failure for 40% of the "
        "card time. One clause is under test; four cells is what that costs. "
        "w03 is the CONTROL -- moonlight, which is already known to work -- so "
        "a batch-wide failure can be told apart from a rule being wrong.")
    child["failure_predicted_in_advance"] = (
        "FIRST, AND IT IS THE ONE THAT KILLS THE RULE: w02 AND w04 COME BACK "
        "TAN AND PALE ANYWAY. `low sun` and `cold clear air` may be all the "
        "checkpoint needs to reach for dry grass and snow, in which case the "
        "season word was a passenger and what actually carries the ground is "
        "the LIGHT TEMPERATURE itself -- warm light means dry, cold light "
        "means frozen -- and the honest conclusion is that this instrument's "
        "usable non-daylit range is dark skies only, which is what round 5 "
        "already delivered.\n"
        "SECOND: w01 COMES BACK BLUE. The checkpoint may simply draw dusk as "
        "blue whatever the words say, in which case dusk is closed here and "
        "the dark end of the dataset is night and storm, full stop. That is a "
        "clean answer and it retires a cell that has now cost two rounds.\n"
        "THIRD, AND IT WOULD INVALIDATE THE BATCH RATHER THAN ANSWER IT: w03, "
        "the control, fails. v02's words at a new seed producing a plate "
        "without a green plane would mean round 5's passes were seed luck and "
        "nothing in this file's reasoning is supported. Read w03 first.")
    child["clip77_measured_not_estimated"] = (
        "prompt %d of 77, counted offline on animagine's own vocab before this "
        "file was written; negative inherited from the round-4 control at 71 "
        "of 77." % n_p)
    return new_id, child


def main():
    write = "--write" in sys.argv
    out = []
    for tag, seed, lighting, cell_why in VARIANTS:
        new_id, child = build(tag, seed, lighting, cell_why)
        path = "pipeline/jobs/%s.yaml" % new_id
        if write:
            out.append(derive_spec.write(child, path))
            print("wrote %s  seed=%d  %s" % (path, seed, lighting))
        else:
            print("would write %s  seed=%d  %s" % (path, seed, lighting))
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
