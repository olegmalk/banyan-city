"""Round 2 of the sapling dataset's field plates -- derived off the ONE that passed.

ROUND 1 WENT 1 FOR 10 AND THE CAUSE IS NOT THE ONE I PRE-REGISTERED.

Ten plates, seven scenes, five lighting states, three scales
(pipeline/derive_sapling_field_0821.py, contact sheet judged by eye at 1:1):

  p01 tallgrass close   FAIL D2 -- macro of blades, no ground plane
  p02 tallgrass medium  FAIL D3 -- A HOODED FIGURE, white mask, dark cloak
  p03 dry sunset close  FAIL D2 -- pure orange grass texture
  p04 dry sunset medium FAIL D2 -- a dune of dry grass, nothing to root in
  p05 creek close       FAIL D1 -- painterly/photographic, not cel
  p06 hillside medium   FAIL D3 -- A GIANT BIRD filling the frame
  p07 mist close        FAIL D2 -- grass silhouettes against the sun
  p08 dirt medium       FAIL D2 -- AN EGG in a nest, dead centre
  p09 meadow WIDE       PASS -- clean drawable ground, cel, light has direction
  p10 path close        FAIL D2 -- macro of dry grass

THE COMMON CAUSE IS THE FRAMING WORD ON A SUBJECT-LESS PROMPT. `close-up` and
`medium shot` need something to be close to. With every figure tag stripped and
`no humans` in their place, the only thing left to frame is the GRASS, so the
sampler magnified it -- six of the ten came back as macro texture studies with
no ground plane at all. The framing word did not choose a camera distance, it
chose a subject.

AND MY PRE-REGISTERED FAILURE WAS THE MIRROR IMAGE OF THE TRUTH. I wrote:
"`no humans` DOES NOT BUY AN EMPTY FRAME, IT BUYS A LANDSCAPE ... if all six
come back as wide painterly country, the fix is not a seventh wording." The
landscape is the thing that WORKED. p09 is the only cell whose framing implies
a distance from which ground is visible, it is the cell the spec argued against
filing, and it is the only usable plate in the batch. Recorded rather than
smoothed over: the batch was filed with the wide cell as the sacrificial test
of a closed question, and the closed question re-opened in the other direction.

SO ROUND 2 FREEZES p09's FRAMING AND MOVES ONE CLAUSE. `wide shot, low angle`
is byte-identical in all eight cells; the scene-and-lighting phrase is the only
thing that varies. THE SCALE AXIS THE GATE ASKS FOR NO LONGER COMES FROM THE
SAMPLER -- it comes from CROPPING these plates, which beat 09 measured surviving
downstream at 2.157x LANCZOS with 105% of frame 1's high-frequency energy at
f121. Asking a diffusion model for a magnification bought ten minutes of macro
grass; a crop is deterministic, free, and already proven in this tree.

SECOND FINDING, FILED AND NOT FIXED HERE: `no humans` PLUS a nine-term figure
ban did NOT hold. Two of ten produced a creature anyway -- a hooded masked
figure and a bird. That is this tree's negatives failing to hold position for
the fourth time, and it is why bar clause D3 deletes rather than crops. No
negative change is attempted in round 2: the lever that has failed four times
is not the lever to pull, and one passing cell is not enough evidence to
re-author the ban list.

Run:  python3 pipeline/derive_sapling_field_r2_0821.py [--write]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clip_token_count  # noqa: E402
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402
from derive_sapling_field_0821 import (BAR, assert_under_clip77,  # noqa: E402
                                       stage_step)

PARENT = "pipeline/jobs/ep3-sapfield-p09-0821.yaml"
PARENT_DIRTOK = "sapfield-p09-0821"

QUALITY = "masterpiece, best quality, very aesthetic, no humans"
FRAMING = "wide shot, low angle"   # FROZEN. p09's, byte for byte.

# scene + lighting, the only clause that moves. r01 is p09 itself at a second
# seed, so the batch carries its own reproducibility check instead of assuming
# one clean cell was not luck.
VARIANTS = [
    ("r01", 20260921, "in a green meadow, wildflowers in the distance, clear sky, day",
     "p09's OWN scene words at a new seed. Not filler -- it is the control, and "
     "the batch cannot tell a scene finding from a seed lottery without it. One "
     "clean cell can be luck; the b12 lane learned that at a cost of four "
     "takes."),
    ("r02", 20260922, "in a green meadow, tall grass, clear sky, day",
     "WILDFLOWERS REMOVED. They are the one structure in p09's foreground the "
     "composite would have to paint over, and the negative already bans "
     "`flower` -- p09 passed with its positive and negative contradicting each "
     "other. This cell says which side of that contradiction the ground plane "
     "was on."),
    ("r03", 20260923, "in a green meadow, tall grass, sunset, orange sky, long shadows",
     "LIGHTING, warm end. Long shadows give the composite's light-carry step "
     "the strongest gradient to measure. Round 1's sunset cells failed on "
     "framing, not on light, so the lighting axis is untested rather than "
     "closed."),
    ("r04", 20260924, "in a green meadow, tall grass, morning, mist, backlighting",
     "LIGHTING, cool end. Backlight is the hardest case for the crescent "
     "highlight b19 authored against a front-lit plate."),
    ("r05", 20260925, "on a grassy hillside, blue sky, white clouds, midday",
     "TERRAIN. Round 1's hillside cell returned a bird, so the scene words are "
     "unjudged -- the cell failed on D3 before its ground plane could be read."),
    ("r06", 20260926, "beside a shallow creek, green banks, clear sky, day",
     "TERRAIN, the furthest cell from meadow. Round 1's creek plate was the "
     "only near-miss on dialect rather than on framing, so it is worth one "
     "more at the framing that works."),
    ("r07", 20260927, "in a field of dry grass, autumn, clear sky, day",
     "PALETTE. The composite samples its greens FROM THE PLATE, so a plate with "
     "no green in it is the test of whether the instrument can put a green "
     "sapling in a dry field or whether it will tint it straw."),
    ("r08", 20260928, "on a dirt path, green field, late afternoon, warm light",
     "THE UNVEGETATED STRIP. A path gives the composite a clean place to root "
     "that is bought by the scene words instead of hoped for from the sampler "
     "-- the D2 clause the whole of round 1 lost."),
]


def build(tag, seed, scene, cell_why):
    new_id = "ep3-sapfld2-%s-0821" % tag
    dirtok = "sapfld2-%s-0821" % tag
    prompt = "%s, %s, %s" % (QUALITY, scene, FRAMING)
    n_p = assert_under_clip77("%s prompt" % new_id, prompt)

    # r01 is p09's prompt to the byte -- it is the seed control -- so it
    # INHERITS the payload rather than overriding it with a copy. derive_spec
    # refuses a byte-identical override and it is right to: passing the
    # parent's text through your own hand is still inheritance, and pretending
    # otherwise would put a fake "the_one_variable" on the control cell.
    parent_prompt = derive_spec.load(
        os.path.join(derive_spec.REPO, PARENT))["payload"]
    inherits_prompt = any(
        k.endswith("prompt.txt") and v.strip() == prompt.strip()
        for k, v in parent_prompt.items())

    overrides = {"seed": seed, "key:priority": 39}
    if not inherits_prompt:
        overrides["payload:prompt.txt"] = prompt

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "sapling-dataset lane, 2026-08-21 round 2",
            "consumer":
                "THE SAPLING LoRA DATASET's scene axis, and the crop that "
                "gives it a scale axis. pipeline/lora/README.md wants >=20 "
                "composited saplings across distinct scenes, scales and "
                "lighting; round 1 returned exactly one usable ground plane "
                "out of ten and this batch buys the breadth off the cell that "
                "worked. Nothing here enters a cut and nothing here is a "
                "beat.",
            "success":
                "One 832x1216 png at seed %d, cel dialect, of %s at 'wide "
                "shot, low angle', WITH NO PLANT AND NO FIGURE IN IT and a "
                "clean drawable ground plane in the lower centre. Judged by "
                "eye at 1:1 against the five D-clauses, as one contact sheet "
                "with its seven siblings." % (seed, scene),
            "why":
                "%s\n\nROUND 1 WENT 1 FOR 10 AND THE FRAMING WORD WAS THE "
                "CAUSE. `close-up` and `medium shot` on a prompt with every "
                "figure tag stripped had nothing to be close to, so the "
                "sampler magnified the grass: six of ten came back as macro "
                "texture with no ground plane. p09, the only wide cell and "
                "the one the spec argued against filing, is the only plate "
                "worth keeping. Its framing is frozen here and the scene "
                "clause is the single variable." % cell_why,
        },
        overrides=overrides,
        retoken=[(PARENT_DIRTOK, dirtok)],
        by="pipeline/derive_sapling_field_r2_0821.py",
    )

    child["steps"].insert(0, stage_step(dirtok))
    child["bar"] = BAR.replace("TEN PLATES", "EIGHT PLATES").replace(
        "nine siblings", "seven siblings")
    child["the_one_variable"] = (
        "THE SCENE-AND-LIGHTING CLAUSE (%r). The framing clause 'wide shot, "
        "low angle' is p09's byte for byte and is FROZEN across all eight; so "
        "are the quality prefix, `no humans`, the negative, the checkpoint, "
        "the size, the steps, the cfg, the nocontrol arm and its 0.45 scale. "
        "The seed walks so the set is not seed-degenerate." % scene)
    child["this_cell"] = cell_why
    child["round_1_result_that_bought_this"] = (
        "1 OF 10. p01/p03/p04/p07/p10 lost D2 to macro framing, p05 lost D1 to "
        "a painterly dialect, p02 returned a hooded masked figure and p06 a "
        "giant bird (D3), and p09 -- meadow, wide shot, low angle -- passed. "
        "The framing word, not the scene word, separates them: every close and "
        "medium cell failed and the only wide cell passed."
    )
    child["the_scale_axis_moved_off_the_sampler"] = (
        "THE GATE WANTS DISTINCT SCALES AND THIS BATCH DOES NOT ASK FOR ANY. "
        "Round 1 asked the sampler for magnification and got macro grass six "
        "times. Scale now comes from CROPPING these wide plates, which beat 09 "
        "measured surviving downstream at 2.157x LANCZOS with 105% of frame "
        "1's high-frequency energy at f121. A crop is deterministic and $0; a "
        "framing word on a subject-less prompt is a lottery this batch already "
        "lost."
    )
    child["my_prediction_was_backwards_and_it_is_on_the_record"] = (
        "derive_sapling_field_0821 pre-registered 'FIRST AND MOST LIKELY: "
        "`no humans` DOES NOT BUY AN EMPTY FRAME, IT BUYS A LANDSCAPE', and "
        "filed the wide cell as the sacrificial test of a question the "
        "ep2-b16-field batch was thought to have closed. THE LANDSCAPE IS THE "
        "THING THAT WORKED. Kept here rather than quietly replaced, because a "
        "prediction that is only recorded when it lands is not a prediction."
    )
    child["negatives_failed_again_and_are_NOT_touched_here"] = (
        "`no humans` in the positive plus a nine-term figure ban in the "
        "negative still returned a hooded figure (p02) and a bird (p06) -- "
        "this tree's negatives failing to hold position for the fourth time. "
        "NO NEGATIVE CHANGE IS ATTEMPTED: the lever that has failed four times "
        "is not the lever to pull, and one passing cell is not the evidence to "
        "re-author a ban list on. The guard that holds is bar clause D3, which "
        "DELETES a frame carrying a figure rather than curating it -- which "
        "also means p02 and p06 are deleted, not cropped."
    )
    child["failure_predicted_in_advance"] = (
        "FIRST: THE GROUND PLANE IS TOO FAR AWAY. `wide shot, low angle` buys "
        "a visible ground, but p09's usable strip is mid-frame, not the lower "
        "centre the composite roots into. If the passing cells all put their "
        "clean ground at the horizon, the fix is the CROP -- which this batch "
        "has already committed to for scale -- and not a ninth wording.\n"
        "SECOND: THE CONTROL SPLITS FROM p09. r01 is p09's own words at a new "
        "seed. If r01 fails, the round-1 pass was a seed lottery and the "
        "framing finding is unproven; that would be worth knowing at a cost of "
        "three minutes and it is why the control is in the batch.\n"
        "THIRD: r07, THE DRY FIELD, COMES BACK WITH NO GREEN AND THE COMPOSITE "
        "TINTS THE SAPLING STRAW. The instrument samples its palette from the "
        "plate by design. That is a finding about how far the scene axis can "
        "be pushed before the palette rule breaks, and it is cheaper to learn "
        "on one plate than at frame twenty."
    )
    child["clip77_measured_not_estimated"] = (
        "prompt %d of 77, counted offline on animagine's own vocab before this "
        "file was written. The negative is p09's, inherited unchanged at 71 of "
        "77." % n_p)
    return new_id, child


def main():
    write = "--write" in sys.argv
    out_paths = []
    for tag, seed, scene, cell_why in VARIANTS:
        new_id, child = build(tag, seed, scene, cell_why)
        out = "pipeline/jobs/%s.yaml" % new_id
        if write:
            out_paths.append(derive_spec.write(child, out))
            print("wrote %s  seed=%d  %s" % (out, seed, scene))
        else:
            print("would write %s  seed=%d  %s" % (out, seed, scene))
    if not write:
        print("\n(dry run -- pass --write)")
        return 0
    for p in out_paths:
        derive_fetch_guard.assert_fetch_urls_resolve(
            p, must_hold=("controlnet_plate.py",))
    print("\nfetch guard: all %d spec(s) resolve" % len(out_paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
