#!/usr/bin/env python3
r"""BEAT 01, PLATE-SIDE: four FIELD plates with NO PLANT IN THEM.

WHY THIS EXISTS, AND WHY IT IS NOT THE JOB THAT WAS ASKED FOR. The route call
on 2026-08-21 was "plate-side: draw the canon two-leaf sapling at FINAL size on
b01's field with beat16_sapling_composite, 0.30 naturalize". That is the right
route and this is its missing first rung. beat16_sapling_composite cannot be
pointed at b01's existing plate, and the reason is MEASURED rather than
guessed:

  region                 min    p05    med    p95
  sapling STEM          38.3   55.5  130.5  152.2
  grass blade left      68.3   79.8  114.9  151.9
  field mid, no plant   79.4   92.8  140.4  159.4
  bright field UPPER    76.4   81.6   89.1  106.0

The compositor's `--erase-box` is a luma flood: it seeds on the weed's own ink
and grows through pixels below `--erase-lum`. That primitive assumes a DARK
plant on a BRIGHT field, which is what beats 15/16/19 had. b01 is BACKLIT, and
on this plate the ordering is inverted -- the upper field (median 89.1) is
DARKER than the sapling stem it would have to distinguish (median 130.5), and
the foreground grass silhouettes (114.9) sit between them. There is no
threshold that separates subject from field, and the run confirms it: the flood
escapes into the grass and returns a 68,542 px matte for a stem, then C0c
refuses because the matte is touching the box edge rather than being contained
by it.

AND MASKING INSTEAD OF ERASING DOES NOT RESCUE IT, on this tree's own finding:
a 0.30 pass runs 12 of 40 steps from a latent that still carries the init, so
it PRESERVES a plant rather than removing one (b16 sapcomp, and the sentence is
in beat16_sapling_composite.py's own --erase-box help). Drawing the final-size
sapling over the small one would leave the small one's leaves standing at
y 645-760 outside the new stem's silhouette. Two plants in frame breaks
`sapling-two-leaves` (founder, 2026-08-16).

SO THE PLANT HAS TO BE ABSENT FROM THE PLATE, not removed from it -- which is
exactly what step 1 of the beat-16 restage did (derive_b16_field_0820.py) and
why that restage is the pattern being followed rather than improvised on.

THE ONE VARIABLE against the parent is the PROMPT. Same script, same arm
(nocontrol), same scale, same steps, same publish. Four seeds of one recipe.

THE PROMPT IS IN THE MODEL'S OWN DIALECT, and `no humans` leads the POSITIVE
with the person nouns kept OUT of the negative. That is not a style choice: it
is node 001 beat 6's round-5 finding, where negating `humans` while deleting
`no humans` from the positive drove girls from 2/4 to 3/4 on the round meant to
remove them. animagine-xl-3.1 declares the presence of people with a positive
tag.

ROUND 1 RAN AND IS THE REASON THIS RECIPE CHANGED. Four seeds were queued;
the first landed in 9.6 s and was opened before the rest were let through,
which is the one-sample rule doing its job. All three that rendered came back
as SUNSET VISTAS -- sky, clouds, a distant hill line and a sun disc in every
one. b01's approved plate has NO SKY AND NO HORIZON AT ALL: it is an intimate
hazy close field with a light shaft, and the founder approved that look on
2026-08-21 by keeping the take that carries it. So round 1 passed P1 (no
plant), P2 (no figure) and P4 (backlit amber) and missed the only clause that
made the plate usable.

THE CAUSE IS `scenery`, AND IT WAS MINE. On Danbooru `scenery` IS the
landscape-shot tag -- it does not mean "outdoors", it means the wide vista that
came back three times out of three -- and `evening` and `light rays` compounded
it into a sun disc. Round 2 drops all three from the positive and negates the
vista furniture directly (sky, cloud, horizon, sun, sunset, mountain, scenery,
landscape). The plant negatives are unchanged because they worked: not one of
the three had a seedling in it.

ROUND 2 IS ONE SEED, NOT FOUR. Four seeds of an unproven recipe is the mistake
round 1 made; the seeds cost 10 s each but the review does not, and three more
pictures of the wrong framing is not iteration.

ROUND 2 RAN AND OVERCORRECTED, AND THAT PAIR IS THE REAL FINDING. Dropping
`scenery`/`evening`/`light rays` and negating the vista furniture WORKED on the
clause it targeted -- no sky, no cloud, no horizon, no sun disc. But with no
distance clause left at all the model drew a MACRO WALL OF GRASS filling the
frame edge to edge: no negative space, no light shaft, no hazy mid-band, and
nowhere to stand a stem. Round 1 was too far away, round 2 is too close, and
neither is a plate the composite can use.

SO THE LEVER IS DISTANCE, AND THIS LANE SHOULD STOP HERE RATHER THAN FIND THAT
OUT A THIRD TIME. pipeline/derive_sapling_field_r4_0821.py is a ladder already
four rounds deep on EXACTLY this problem -- "a plate a cel seedling can be
drawn onto standing straight up" -- and it has already established the two
things these two rounds just re-derived: that the DISTANCE clause is the lever
(its r02), and that naming a distant landform is what returns a rootable ground
plane (its r03). It has also retired `low angle` as a fisheye generator, which
is a fourth round this lane has not paid for and would otherwise have walked
into.

THE HONEST NEXT MOVE IS NOT A ROUND 3 HERE. It is to take b01's requirement --
the approved look has NO horizon, which is the one place b01 differs from that
ladder's target -- to the sapling-field lane as a cell in ITS matrix, rather
than running a parallel ladder against the same model with the same lever and a
different file name.

WHAT THIS DOES NOT DO. It does not choose a plate, it does not composite, and
it does not touch the cut. The founder reverted beat 01 by hand on 2026-08-21
and the fignonly take ships; nothing here is proposed as a swap. He asked for
more iteration on this beat and these are the plates that iteration needs.

$0 beyond ~3 GPU-minutes each on the box.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402
import sd_prompt  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b16-field-f1-0820.yaml"
STAGED_FILE = "pipeline/controlnet_plate.py"
BOX = "rtx5090"

# `no humans` FIRST (node 001 b06 r5), then the scene, then the light, then
# depth. No plant noun anywhere in the positive: the composite draws the plant,
# and a field that arrives with its own seedling is a field that cannot be used.
POSITIVE = ("no humans, grass, tall grass, field, outdoors, backlighting, "
            "glowing, orange theme, blurry, depth of field, blurry foreground, "
            "masterpiece, best quality, very aesthetic")
# Person nouns deliberately absent -- see the module docstring. The plant
# negatives name only CULTIVATED/woody forms, never `leaf` or `plant`, because
# the grass is made of both and this plate is nothing but grass.
NEGATIVE = ("lowres, worst quality, low quality, text, watermark, signature, "
            "jpeg artifacts, flower, tree, branch, sapling, seedling, sprout, "
            "potted plant, bush, shrub, fruit, "
            "sky, cloud, horizon, sun, sunset, mountain, scenery, landscape")

# (tag, seed) -- four seeds of ONE recipe. The recipe is the variable that
# already moved; the seed is the only thing left to sample.
VARIANTS = [("r2s1", 20260861)]


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stage_src(tags) -> int:
    """Put controlnet_plate.py where every step's argv already says it is.

    Verified by reading the sha BACK OFF THE BOX. A file that is missing on the
    box is invisible to every guard between here and the GPU.
    """
    local = os.path.join(REPO, STAGED_FILE)
    want = _sha256(local)
    print("staging %s  sha256 %s" % (STAGED_FILE, want[:12]))
    bad = []
    for tag in tags:
        d = "C:\\banyan-farm\\b01field-%s-0821\\src\\pipeline" % tag
        subprocess.run(["ssh", "-o", "ConnectTimeout=20", BOX,
                        'if not exist "%s" mkdir "%s"' % (d, d)], check=False)
        r = subprocess.run(
            ["scp", "-o", "ConnectTimeout=20", local,
             "%s:C:/banyan-farm/b01field-%s-0821/src/pipeline/controlnet_plate.py"
             % (BOX, tag)], capture_output=True, text=True,
            encoding="utf-8", errors="replace")
        if r.returncode:
            bad.append("%s scp rc=%d %s" % (tag, r.returncode, r.stderr.strip()))
            continue
        back = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=20", BOX,
             'powershell -NoProfile -Command "(Get-FileHash -Algorithm SHA256 '
             "'C:\\banyan-farm\\b01field-%s-0821\\src\\pipeline\\controlnet_plate.py'"
             ').Hash"' % tag], capture_output=True, text=True,
            encoding="utf-8", errors="replace")
        got = (back.stdout or "").strip().lower()
        if got[:64] != want[:64]:
            bad.append("%s sha on box %s != %s" % (tag, got[:12], want[:12]))
        else:
            print("  %s staged and verified" % tag)
    for b in bad:
        print("!! %s" % b)
    return 1 if bad else 0


def main() -> int:
    write = "--write" in sys.argv
    if "--stage" in sys.argv or write:
        rc = stage_src([t for t, _ in VARIANTS])
        if rc:
            print("!! staging failed -- not writing specs for a step whose "
                  "script is not on the box.")
            return rc
        if "--stage" in sys.argv and not write:
            return 0

    n = sd_prompt.negative_tokens(POSITIVE)
    if n > 77:
        print("!! positive = %d tokens, over the 77 the encoder reads" % n)
        return 1
    print("positive %d tokens, negative %d tokens"
          % (n, sd_prompt.negative_tokens(NEGATIVE)))

    for tag, seed in VARIANTS:
        new_id = "ep2-b01-field-%s-0821" % tag
        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "the ship-repair lane, 2026-08-21",
                "consumer": (
                    "STEP 1 OF THE BEAT-01 PLATE-SIDE ROUTE. The cold open's "
                    "shipping take (01-cold-open-LTX-fignonly-s20260840) is 7 "
                    "of 8 scored clauses and fails G5a because the SAPLING and "
                    "the SHAFT are redrawn across the clip. Its own verdict "
                    "closed the prompt-side door -- the six plant-growth "
                    "negatives moved the sapling NCC 0.092 -> 0.055, i.e. "
                    "nothing -- and named two routes left, plate-side and "
                    "compositor-side. This is plate-side's first rung: a field "
                    "with NO PLANT IN IT, so beat16_sapling_composite can draw "
                    "the canon two-leaf sapling at FINAL SIZE and leave the "
                    "motion model nothing to grow. NOT A SWAP. The founder "
                    "reverted beat 01 by hand on 2026-08-21 and the fignonly "
                    "take ships; he asked for more iteration on this beat and "
                    "these are the plates it needs. R4 is his."),
                "success": (
                    "ONE 832x1216 png of a backlit grass field with NO PLANT, "
                    "NO FIGURE and NO FRUIT anywhere in it, carrying b01's "
                    "approved look: warm amber backlight, a visible light "
                    "shaft, dark grass silhouettes across the foreground, "
                    "shallow depth of field. JUDGED BY EYE against the "
                    "shipping take's own frame 0, because the thing being "
                    "matched is a look the founder approved and there is no "
                    "instrument for that. A plate with any seedling, sprout or "
                    "fruit in it is a FAIL for this purpose however pretty it "
                    "is -- the whole point is an empty ground plane for the "
                    "composite -- and so is a plate with no clear root line, "
                    "because the composite needs a place to stand the stem."),
                "why": (
                    "$0 beyond ~3 GPU-minutes, no download, nothing to fetch. "
                    "THE ONE VARIABLE AGAINST THE PARENT IS THE PROMPT: same "
                    "controlnet_plate.py, same nocontrol arm, same scale 0.45, "
                    "same publish. Four seeds of one recipe, because the "
                    "recipe is what changed and the seed is the only thing "
                    "left to sample."),
            },
            overrides={
                "payload:prompt.txt": POSITIVE,
                "payload:negative.txt": NEGATIVE,
                "seed": seed,
                "key:priority": 32,
            },
            retoken=[("b16field-f1-0820", "b01field-%s-0821" % tag),
                     ("ep2-b16-field-f1-0820", new_id)],
            extra={
                "the_one_variable": (
                    "prompt.txt and negative.txt. Everything else -- script, "
                    "arm, scale, control assertion, steps, out dir -- is the "
                    "parent's, byte for byte."),
                "why_the_erase_route_was_not_taken": (
                    "MEASURED, not assumed. beat16_sapling_composite's "
                    "--erase-box is a luma flood seeded on the plant's ink and "
                    "grown through pixels below --erase-lum, which assumes a "
                    "dark plant on a bright field. On b01's backlit plate that "
                    "ordering is inverted: upper field median luma 89.1, "
                    "sapling stem 130.5, foreground grass 114.9. No threshold "
                    "separates them, and the run proves it -- the flood "
                    "escapes into the grass, returns 68,542 px of matte for a "
                    "thin stem, and C0c refuses. Masking without erasing does "
                    "not rescue it either: a 0.30 pass preserves a plant "
                    "rather than removing one, so the small sapling's leaves "
                    "would stand at y 645-760 beside the new one and break "
                    "`sapling-two-leaves`."),
                "bar": {
                    "how_it_is_judged": (
                        "BY EYE, and this is declared rather than dressed up. "
                        "The target is a look the founder approved on "
                        "2026-08-21 by choosing the take that carries it; this "
                        "repo has no instrument for 'matches that look'. What "
                        "IS checkable is checked below."),
                    "P1_no_plant": (
                        "SCORED BY EYE, conjunctive with the rest. No "
                        "seedling, sprout, stem, flower or fruit anywhere in "
                        "frame. This is the clause the plate exists for."),
                    "P2_no_figure": "SCORED BY EYE. No person, no goblin.",
                    "P3_root_line_exists": (
                        "SCORED BY EYE. There is a readable grass/ground line "
                        "a vertical stem could be stood on, in the lower third "
                        "and not curved like a fisheye horizon. Round 4 of the "
                        "sapling-field ladder retired `low angle` for exactly "
                        "this reason; the framing here inherits that."),
                    "P4_backlit_amber": (
                        "SCORED BY EYE. Warm backlight with a visible shaft, "
                        "not flat daylight."),
                    "not_scored": (
                        "Grass density, bokeh count and shaft angle are NOT "
                        "bars. Naming them as bars would be inventing "
                        "precision; they are picks, and the pick is the "
                        "founder's."),
                },
                "script_authority_note": (
                    "Node 002b-first-citizen, approved_by: founder, "
                    "approved_on: 2026-08-03. This renders a BACKGROUND PLATE, "
                    "no character and no dialogue. Silent, $0, no voice "
                    "synthesis, no episode assembly, nothing enters the cut "
                    "without the founder's eye under R4."),
            },
            by="pipeline/derive_b01_field_0821.py",
        )
        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        if write:
            derive_spec.write(child, out)
            print("wrote %s  seed %d" % (out, seed))
        else:
            print("would write %s  seed %d" % (out, seed))
    if not write:
        print("\n(dry run -- pass --write to author the specs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
