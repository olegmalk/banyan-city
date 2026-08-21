"""Batch A of the SAPLING LoRA dataset's goblin-free field plates.

WHAT THIS IS FOR, and it is not a beat.

`pipeline/lora/README.md` (the sapling gate, committed c8eeb81e) blocks the
sapling LoRA dataset on VARIETY, not on count:

    "The gate is >=20 composited saplings spanning distinct scenes, scales
     and lighting -- and the growth ladder (genomes/sapling/style.md:152-159,
     ~15 cm and 2 leaves in 001 rising to ~1.6 m and 6 leaves by 006a) means
     scale and leaf count must stay *variables in the captions*, never baked
     in, or one LoRA cannot serve seven episodes."
    "~23 frames across five near-identical field scenes is below the variety
     floor a character LoRA needs."

Every one of those ~23 lives on a beat plate WITH THE SCAVENGER IN IT, on five
near-identical tall-grass scenes. Both facts are disqualifying here for the
same reason twice over: a subject LoRA trained on frames that share a backdrop
learns the backdrop into the trigger token, and a figure in every frame teaches
the trigger a figure. So the dataset needs plates that are FIELD AND NOTHING
ELSE, across scenes and lighting the episode's five composites do not span.

THESE PLATES ARE STEP 1 OF THREE and no picture here is the dataset:
  (1) THIS -- empty ground planes by text, no plant, no figure.
  (2) pipeline/beat16_sapling_composite.py draws the canon two-leaf sapling
      into the passing plates at varied root/height/tilt -- the growth ladder's
      own heights -- with the plate's measured light carried in. $0, no GPU.
  (3) one 0.30 inpaint per composite to naturalise it, then captions and
      pipeline/lora/build_dataset.py sapling.

WHY THE PROMPT IS NOT THE PARENT'S TAIL, AND WHY THE NEGATIVE IS NOT BYTE-
IDENTICAL EITHER. Two measured results, not preferences:

  * `scenery` KILLED THE LAST FIELD BATCH. work-ladder-0819.md, appended
    2026-08-20: ep2-b16-field-f1..f4-0820 all four came back "landscape
    illustration -- photographic bokeh, painterly rendering, and on f1 and f4
    monumental architecture nobody asked for", failing F5 (cel dialect) and F1
    (clean near foreground) across the batch REGARDLESS OF FRAMING. "`scenery`
    bought a vista where the beat needs a shot." The word does not appear
    below. The ratified recipe's own location idiom -- `in tall grass` -- does.
  * The dialect words that failure names (bokeh, painterly, photographic) go
    into the NEGATIVE, and so do the figure words. That is a deliberate
    departure from the parent's byte-identical negative and it is bought by a
    hard constraint, not by taste: THIS LANE MAY NOT RENDER THE GOBLIN (his age
    is R4-gated), so the positive carries `no humans` and zero figure tags and
    the negative names the figure anyway. Negatives in this tree have failed to
    hold position three for three, which is why the bar below REJECTS any frame
    with a figure in it rather than trusting the ban.

WHAT IS UNCHANGED FROM THE RATIFIED RECIPE ep2-b04-tilefix-w2-0820: checkpoint,
832x1216, steps, cfg, the `nocontrol` arm and its 0.45 scale, the quality
prefix, the publish glob (this parent is the one where the -nocontrol.png glob
was FIXED; the -hintskel.png bug stranded eight renders on the card).

THE STAGE STEP IS ADDED HERE ON PURPOSE. The parent and its twelve tileset
siblings only ever ran because a human scp'd controlnet_plate.py into
`<payload dir>\\src\\pipeline\\` by hand -- derive_b16_field_0820.py:70-82
records the rc=1 "can't open file" that discovered it. This lane will not be
awake to scp anything, so each child fetches the interpreter over https with a
sha256 assertion, on the jerry-scene-0821 pattern. The URL names
`farm-out/jerry-skel-assets-0820/`, which does NOT contain a job id, so
derive_spec's retokeniser cannot rewrite it into a directory nobody wrote --
the exact failure derive_fetch_guard.py exists for. Asserted anyway.

Run:  python3 pipeline/derive_sapling_field_0821.py [--write]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402
import derive_fetch_guard  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b04-tilefix-w2-0820.yaml"
PARENT_DIRTOK = "b04tilefix-w2-0820"

# The interpreter, fetched instead of hand-staged. Committed on main at
# 894b6214 and byte-identical to pipeline/controlnet_plate.py right now.
CNET_URL_DIR = ("https://raw.githubusercontent.com/olegmalk/banyan-city/"
                "main/farm-out/jerry-skel-assets-0820/")
CNET_SHA = "ece54f687d892d1fb1df17211331919bfcb04faac4fe0ee6aa9b0bb231adcc32"

QUALITY = "masterpiece, best quality, very aesthetic, no humans"

NEGATIVE = (
    # the parent's, byte for byte, up to `pale skin` --
    "lowres, worst quality, low quality, text, watermark, pointy ears, "
    "long pointy ears, elf, monster boy, pointy nose, dot nose, human face, "
    "wrinkled skin, old man, thick eyebrows, hair, beard, child, chibi, "
    "grey skin, pale skin, 2boys, "
    # -- and then the two bans this job's own constraints buy:
    # FIGURE, because the goblin is R4-gated and no frame here may carry him.
    "1boy, 1girl, 1other, solo, people, silhouette, goblin, animal, "
    # PLANT, because a plate whose foreground already holds a structure makes
    # the 0.30 pass argue with it instead of finishing the drawn sapling
    # (composite-init-pattern, and b15's weed cost beat 16 an erase-and-fill).
    "flower, tree, bush, shrub, sapling, seedling, potted plant, "
    # DIALECT, the measured cause of the ep2-b16-field-f1..f4 batch failure.
    "scenery, landscape, bokeh, blurry, depth of field, painterly, "
    "photorealistic, photo, 3d, realistic, architecture, ruins, building"
)

# scene/lighting x scale. One variable moves per cell from p01, which is the
# ratified recipe's own location and the batch's control.
#   scene words  |  scale words
VARIANTS = [
    ("p01", 20260901,
     "in tall grass, sunlight, day",
     "close-up, low angle, ground level",
     "CONTROL. The ratified recipe's own location clause and the tightest "
     "scale. Nearest cell to a picture this checkpoint has returned fourteen "
     "times; if THIS one breaks dialect the cause is `no humans`, not the "
     "scene words, and the whole route changes."),
    ("p02", 20260902,
     "in tall grass, sunlight, day",
     "medium shot, eye level",
     "SCALE, one variable from p01. The ground plane a 55-90 cm sapling "
     "needs -- ep3's node 003b sits at ~55 cm, three leaves."),
    ("p03", 20260903,
     "in a field of dry grass, sunset, orange sky, long shadows",
     "close-up, low angle, ground level",
     "LIGHTING, one variable from p01. Long shadows give the composite step "
     "the strongest light direction to measure and carry into the plant; a "
     "flat plate makes that step a no-op."),
    ("p04", 20260904,
     "in a field of dry grass, sunset, orange sky, long shadows",
     "medium shot, eye level",
     "The p03 x p02 corner, so the two axes are crossed and not merely "
     "sampled."),
    ("p05", 20260905,
     "beside a shallow creek, wet stones, dappled sunlight, day",
     "close-up, low angle, ground level",
     "SCENE, the furthest cell from tall grass. Wet stone and dapple are the "
     "hardest palette for the composite's plate-sampled greens; if the drawn "
     "sapling cannot be lit into this one, that is a finding about the "
     "instrument and it is cheaper to learn here than at frame twenty."),
    ("p06", 20260906,
     "on a grassy hillside, blue sky, white clouds, midday",
     "medium shot, eye level",
     "SCENE + a horizon, without the word that bought a vista last time. The "
     "hillside is the one cell where a high horizon is asked for by the "
     "ground plane rather than by a framing word."),
    ("p07", 20260907,
     "in tall grass, morning, mist, backlighting",
     "close-up, low angle, ground level",
     "LIGHTING, the cool end. Backlight is the hardest case for the "
     "composite's crescent highlight -- b19 authored that highlight against "
     "a front-lit plate -- so it is the cell most likely to expose the "
     "instrument rather than the words."),
    ("p08", 20260908,
     "on bare dirt ground, patchy grass, overcast, soft light",
     "medium shot, eye level",
     "THE FLAT CELL, filed deliberately against D4. If a directionless plate "
     "produces a composite that still reads as belonging, the light-carry "
     "step is doing less than its docstring claims and that is worth one "
     "plate to find out."),
    ("p09", 20260909,
     "in a green meadow, wildflowers in the distance, clear sky, day",
     "wide shot, low angle",
     "THE WIDEST CELL, and the one the ep2-b16-field batch's failure argues "
     "against. `wide shot` without `scenery` is the untested half of that "
     "finding: if p09 holds the cel dialect, the vista was the word and not "
     "the framing, and the 1.2m-1.6m end of the growth ladder gets a ground "
     "plane. If it breaks, the finding is confirmed at a cost of 3 minutes."),
    ("p10", 20260910,
     "beside a dirt path, tall grass, late afternoon, warm light",
     "close-up, low angle, ground level",
     "SCENE, and the only cell with a MAN-MADE edge in it. A path gives the "
     "composite a clean unvegetated strip to root into, which is the D2 "
     "clause bought by the scene words instead of hoped for from the "
     "sampler."),
]

BAR = """TEN PLATES, JUDGED AS ONE CONTACT SHEET, BY EYE AT 1:1. THERE IS NO
PLANT AND NO FIGURE IN ANY OF THESE PICTURES AND BOTH ABSENCES ARE CORRECT.
  D1 CEL, NOT PHOTO, NOT PAINTING. Flat fills, clean ink linework, the
     episode's dialect. This is the clause the ep2-b16-field batch lost all
     four on, and it is the first one read. Bokeh, painterly rendering or a
     photographic ground plane REJECTS the plate -- you cannot draw a sharp
     cel seedling into a soft foreground without it reading as a decal.
  D2 A CLEAN DRAWABLE GROUND PLANE in the lower centre, wide and tall enough
     to root a sapling at plate scale. Blades of grass crossing it are fine.
     A rock, a flower, a shrub, a drawn plant or any structure is NOT: the
     0.30 pass PRESERVES a structure it finds in the init (12 of 40 steps from
     a latent that still carries it), so the composite would have to fight it.
  D3 ZERO FIGURES. Not a goblin, not a human, not an animal, not a silhouette
     on the horizon. A plate with any figure in it is REJECTED AND DELETED,
     not cropped -- this lane may not render the scavenger and a frame that
     contains him is not curated into a training set.
  D4 THE LIGHT HAS A DIRECTION. beat16_sapling_composite.py measures the
     plate's own low-pass luminance gradient and carries it into the drawn
     plant. A flat, directionless plate makes that measurement a no-op and
     the composite reads as pasted.
  D5 THE PALETTE IS THIS SHOW'S. The composite samples its greens FROM THE
     PLATE, so an off-palette plate produces an off-palette sapling and the
     frame teaches the LoRA the wrong colour.
NOT SCORED: whether the picture is a good shot. None of these is a shot, none
enters a cut, and none goes near review/ep2-ship-0821. They are ground planes
for an instrument.
NOT SCORED: variety WITHIN a cell. The variety this batch is bought for is
BETWEEN cells and it is measured at the manifest, not here."""


def stage_step(dirtok: str) -> dict:
    """Fetch controlnet_plate.py with a sha assertion. See module docstring."""
    body = (
        "# The parent and its twelve siblings only ran because a human scp'd\n"
        "# this file into <payload dir>\\src\\pipeline\\ by hand. This lane is\n"
        "# not awake to do that, so the job stages its own interpreter and\n"
        "# refuses to reach the GPU if the bytes are not the ones asserted.\n"
        "import hashlib, os, urllib.request\n"
        'base = "%s"\n'
        'dst = r"C:\\banyan-farm\\%s\\src\\pipeline"\n'
        'want = ("controlnet_plate.py", "%s")\n'
        "os.makedirs(dst, exist_ok=True)\n"
        "with urllib.request.urlopen(base + want[0], timeout=120) as r:\n"
        "    blob = r.read()\n"
        "got = hashlib.sha256(blob).hexdigest()\n"
        "if got != want[1]:\n"
        '    print("!! %%s fetched with sha %%s, expected %%s"\n'
        "          %% (want[0], got, want[1]))\n"
        "    raise SystemExit(1)\n"
        'with open(os.path.join(dst, want[0]), "wb") as fh:\n'
        "    fh.write(blob)\n"
        'print("staged", want[0], got, "->", dst)\n'
        % (CNET_URL_DIR, dirtok, CNET_SHA))
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def build(tag, seed, scene, scale, cell_why):
    new_id = "ep3-sapfield-%s-0821" % tag
    dirtok = "sapfield-%s-0821" % tag
    prompt = "%s, %s, %s" % (QUALITY, scene, scale)

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "sapling-dataset lane, 2026-08-21",
            "consumer":
                "pipeline/lora/manifest-sapling.yaml, WHICH DOES NOT EXIST "
                "YET AND IS THE POINT. The sapling gate in "
                "pipeline/lora/README.md is blocked on variety -- ~23 "
                "composites across five near-identical tall-grass scenes, "
                "every one of them on a plate with the scavenger in it. This "
                "plate is a goblin-free ground plane for step 2, where "
                "beat16_sapling_composite.py draws the canon two-leaf sapling "
                "into it at a height off the growth ladder. NOTHING HERE "
                "ENTERS A CUT and nothing here is a beat: an empty field with "
                "no plant in it is not a shot.",
            "success":
                "One 832x1216 png at seed %d, cel dialect, of %s framed '%s', "
                "WITH NO PLANT AND NO FIGURE IN IT. Judged by eye at 1:1 "
                "against the five D-clauses in `bar`, as one contact sheet "
                "with its nine siblings. A plate carrying any figure is "
                "deleted rather than curated." % (seed, scene, scale),
            "why":
                "%s\n\nThe batch exists because the ep2-b16-field-f1..f4 "
                "batch measured the cause of its own failure -- the word "
                "`scenery` bought a vista and a photographic dialect on all "
                "four plates, independent of framing -- and that word is "
                "absent here. $0 to find out, ~3 minutes of card time, and "
                "the alternative is compositing frame twenty of a training "
                "set onto the same tall-grass backdrop as frames one to "
                "nineteen." % cell_why,
        },
        overrides={
            "seed": seed,
            "payload:prompt.txt": prompt,
            "payload:negative.txt": NEGATIVE,
            "key:priority": 38,
            "key:est_minutes": 3,
            "key:beat": 16,
        },
        retoken=[(PARENT_DIRTOK, dirtok)],
        by="pipeline/derive_sapling_field_0821.py",
    )

    child["steps"].insert(0, stage_step(dirtok))
    child["bar"] = BAR
    child["the_one_variable"] = (
        "THE SCENE/LIGHTING CLAUSE (%r) AND THE SCALE CLAUSE (%r). The quality "
        "prefix, `no humans`, the negative, the checkpoint, the size, the "
        "steps, the cfg, the nocontrol arm and its 0.45 scale are "
        "ep2-b04-tilefix-w2-0820's. The seed walks so the set is not "
        "seed-degenerate." % (scene, scale))
    child["this_cell"] = cell_why
    child["not_a_beat"] = (
        "beat: 16 is carried for the queue's bookkeeping and for one honest "
        "reason beyond it -- beat 16's own restage needs a goblin-free cel "
        "field plate and has never had one, so a passing plate here is "
        "reusable there. It does not make this a beat render: no shot is "
        "authored, no script line is served, nothing is promoted and the "
        "founder's card /review/ep2-b16-leaf-0820 is untouched.")
    child["goblin_free_by_construction"] = (
        "THE SCAVENGER'S AGE IS R4-GATED AND THIS LANE RENDERS NOTHING THAT "
        "CONTAINS HIM. The positive prompt carries `no humans` and not one "
        "figure tag -- no `1other`, no `colored skin`, no `green skin`, no "
        "`bald`, no cloak, none of the seven face tags. The negative names "
        "the figure as a second line of defence only; negatives have failed "
        "to hold position in this tree three for three, so the guard that is "
        "actually load-bearing is bar clause D3: a frame with any figure in "
        "it is REJECTED AND DELETED rather than curated.")
    child["one_sample_rule"] = (
        "SATISFIED BY THE PARENT ON THE RECIPE, AND THE BATCH IS THE SAMPLE "
        "ON THE WORDS. ep2-b04-tilefix-w2-0820 is the ratified still recipe, "
        "sampled fourteen times on 2026-08-20 and re-used unchanged across "
        "twelve Jerry tileset poses and four b16 field plates that are all on "
        "disk. Nothing about the recipe moves here. What moves is the PROMPT, "
        "and a batch of ten backdrops is the plate batch episode-loop-v2 step "
        "1 asks for, at the breadth the gate asks for. THE DIALECT RISK IS "
        "REAL AND IS PRICED: if all ten break cel the loss is 30 minutes of "
        "otherwise-idle card and the route moves to cropping the pre-"
        "composite beat plates, which is written into "
        "failure_predicted_in_advance rather than discovered. p01 is the "
        "control cell and it is the first one read.")
    child["failure_predicted_in_advance"] = (
        "FIRST AND MOST LIKELY: `no humans` DOES NOT BUY AN EMPTY FRAME, IT "
        "BUYS A LANDSCAPE. It is the same gravity `scenery` had -- both are "
        "tags that in the base model's training data label vistas -- and if "
        "all six come back as wide painterly country, the fix is not a "
        "seventh wording: it is to composite onto the PRE-composite beat "
        "plates that are already in the right dialect and crop the figure "
        "out, which costs a crop and no GPU.\n"
        "SECOND: D2, THE CLEAN GROUND PLANE, on the close cells. `tall grass` "
        "at 832x1216 puts its biggest sharpest blades exactly in the near "
        "foreground and that is where the sapling roots. p01/p03/p05 are the "
        "exposed cells; if all three lose D2 and the medium cells hold it, "
        "the dataset's close scale comes from CROPPING a medium plate, which "
        "beat 09 proved survives downstream at 2.157x LANCZOS.\n"
        "THIRD, AND IT WOULD CHANGE THE GATE READING RATHER THAN THE RECIPE: "
        "p05 the creek comes back with water the composite cannot light "
        "against. That is a real answer about how far the scene axis can be "
        "pushed and it is why the furthest cell is in the first six instead "
        "of being discovered at frame twenty.")
    child["gate_this_serves"] = (
        "pipeline/lora/README.md, the sapling section: '>=20 composited "
        "saplings spanning distinct scenes, scales and lighting', with scale "
        "and leaf count kept as caption VARIABLES (trigger `bnysapling`, "
        "pipeline/research/character-lora-sdxl-0820.md section 4) so one LoRA "
        "serves a protagonist who grows 15cm -> 1.6m across seven episodes. "
        "TEN PLATES IS NOT THE GATE and this batch does not claim to clear "
        "it; it is the first ten ground planes of the scene/lighting breadth "
        "the gate asks for and the existing ~23 do not have. Seven distinct "
        "scenes, five lighting states and three scales -- against five "
        "near-identical tall-grass scenes today.")
    child["governance_flag_not_resolved_here"] = (
        "DECISIONS.md item 18 reads 'Never train on the output. No LoRA, no "
        "finetune, no distillation.' The Jerry LoRA is in training under a "
        "later ruling and pipeline/lora/README.md writes the sapling gate as "
        "live work, so item 18 appears superseded in practice -- but this "
        "lane did not resolve it and must not. NOTHING FILED HERE TRAINS "
        "ANYTHING: these are $0 plates, and the composites and captions that "
        "follow are $0 files. Training is a separate, gated act and the "
        "contradiction is raised for the founder before it happens.")
    return new_id, child


def main():
    write = "--write" in sys.argv
    out_paths = []
    for tag, seed, scene, scale, cell_why in VARIANTS:
        new_id, child = build(tag, seed, scene, scale, cell_why)
        out = "pipeline/jobs/%s.yaml" % new_id
        if write:
            p = derive_spec.write(child, out)
            out_paths.append(p)
            print("wrote %s  seed=%d  %s | %s" % (out, seed, scene, scale))
        else:
            print("would write %s  seed=%d  %s | %s"
                  % (out, seed, scene, scale))
            for k, v in child["payload"].items():
                if k.endswith("prompt.txt"):
                    print("    prompt: %s" % v)
    if not write:
        print("\n(dry run -- pass --write)")
        return 0

    # Raises FetchGuardError; a returned set is the pass. The URL below names
    # a directory that carries NO job id, so retoken cannot rewrite it -- but
    # the guard reads the EMITTED file, which is the only check that counts.
    for p in out_paths:
        derive_fetch_guard.assert_fetch_urls_resolve(
            p, must_hold=("controlnet_plate.py",))
    print("\nfetch guard: all %d spec(s) resolve" % len(out_paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
