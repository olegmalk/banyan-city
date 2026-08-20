#!/usr/bin/env python3
r"""BEAT 16: ONE 0.30 pass over the whole-sapling composite. The first init this
beat has ever had.

WHERE THIS SITS. Beat 16 asks for "Close on the sapling's leaf; the scavenger
sits blurred behind it" and the founder's own canon `sapling-cotyledon-shape`
forbids a leaf drawn as a feature. Three wordings failed, a permutation test
came back negative, the big-leaf composite measurably did nothing, and a
four-plate text field batch failed on DIALECT -- `scenery` bought bokeh
landscape illustration where the episode is flat cel. The restage keeps the
brief's relation (plant is subject, he is depth) and drops the clause canon
rules out, and it gets that relation from GEOMETRY rather than from words:
`pipeline/beat16_sapling_composite.py` drew the canon two-leaf sapling LARGE in
the near foreground of a plate that already has him seated behind it.

THE INIT. `farm-out/ep2-b16-sapcomp-0820/16-why-sapcomp-0820.png`, built on
`farm-out/ep2-b15-mac-plate-0819/15-good-listener-mac-plate-r1s1.png` -- the
PRE-composite parent of the b15 plate, so the same flat cel dialect and the same
palette with no finished sapling in it. The weed that plate carries was ERASED
first (b19's flood matte + within-class per-row fill + a grown fringe), because
two plants in frame breaks `sapling-two-leaves` and a 0.30 pass PRESERVES a weed
rather than removing one. Every geometry number is in
`16-why-sapcomp-0820.png.geometry.json`.

WHY THIS IS ONE SAMPLE AND NOT A BATCH. The recipe is `ep2-b03-sapcomp-0820`'s,
which is itself derived from the scored `ep2-b15-sapcomp-0819`: 40 steps, cfg
7.5, strength 0.30, pad-crop 64, blur 8, animagine-xl-3.1 base weights in the
SDXL inpaint pipeline, seed 20260820. Nothing in the recipe changes. THE ONE
VARIABLE IS THE INIT, and the standing rule is one sample before any batch --
this is that sample.

THE NUMBER THAT MAKES THIS DIFFERENT FROM THE BIG-LEAF ATTEMPT. That one failed
because the pass does nothing across 60-80% of a picture: detail inside the
region fell 10.45 -> 9.41 where a working pass holds it and moves it into edges,
across a mask eight times the size of a working one. **This mask is 9.84% of the
frame** while the drawn plant spans 62% of the width and 59% of the height. A
thin object can be the subject of a close-up without asking the pass to
re-render most of the picture, and that is the whole reason the restage is
buildable where the macro was not.

$0, ~5 min, one seed, no download.

Run:  python3 pipeline/derive_b16_sapcomp_0820.py [--write]
"""

from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402
import derive_fetch_guard  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b03-sapcomp-0820.yaml"
PARENT_DIR_TOKEN = "b03sapcomp-0820"
PARENT_ID_TOKEN = "ep2-b03-sapcomp-0820"
NEW_ID = "ep2-b16-sapcomp-0820"
NEW_DIR_TOKEN = "b16sapcomp-0820"

OUT_DIR = "farm-out/ep2-b16-sapcomp-0820"
INIT = "16-why-sapcomp-0820.png"
MASK = "16-why-sapcomp-mask-0820.png"

# The plant is DRAWN. The prompt's job is to finish it in the plate's dialect,
# not to invent it -- 0.30 runs 12 of 40 steps from a latent that still carries
# the drawn structure, so the high-sigma steps where layout is decided never run.
PROMPT = (
    "a young sapling in the foreground with exactly two wide oval leaves with "
    "soft round tips on one thin bare stem, rooted in the grass, close to the "
    "camera and large in frame, with one lean adult goblin man in a patchwork "
    "cloak sitting on the grass behind it, solo, small and further away, sunny "
    "grassy field, detailed cinematic anime, masterpiece, best quality, very "
    "aesthetic"
)

NEGATIVE = (
    "three leaves, four leaves, many leaves, leaflets, extra stalk, multi-node "
    "weed, branching stem, pointed lance leaves, deeply lobed leaves, palmate, "
    "bud, flower, fruit, large tree, thick branch, forest, second plant, two "
    "plants, plant girl, alraune, 2boys, child, chibi, standing, text, "
    "photorealism, 3d render, low quality"
)

BAR = """ONE SAMPLE, JUDGED BY EYE AT 1:1, AND THE FIRST QUESTION IS WHETHER IT
IS THE SHOT -- not whether the pass was busy. Two beats today have now shown
that the model working hard predicts nothing about whether the picture is right.
  S1 IT READS AS BEAT 16. The sapling is the subject of the frame and the
     scavenger is depth behind it. If a viewer's eye lands on him first, the
     restage has not happened and the crop or the plant's scale is the next
     lever, not the prompt.
  S2 EXACTLY TWO LEAVES, on one stem. Canon `sapling-two-leaves`. Three is a
     FAIL however good the drawing is, and so is one.
  S3 AVERAGE LEAVES. Canon `sapling-cotyledon-shape` -- ordinary, plain, the
     shape anyone draws when you say leaf. No lobes, no lance, no exaggerated
     silhouette. The restage exists so the SHOT does not make a leaf a feature;
     a leaf that arrives as a feature anyway defeats the point of it.
  S4 THE PLANT IS DRAWN, NOT PASTED. The pass has to give the blades line
     weight and cel shading in the plate's own dialect. THE FAILURE MODE WITH A
     NUMBER: on the big-leaf attempt the two pictures were the same picture and
     detail inside the region fell 10.45 -> 9.41. If nothing visibly happened,
     say so and stop.
  S5 ONE PLANT IN FRAME. The weed was erased before drawing; if the pass paints
     it back, or paints a third, the erase or the mask is wrong.
  S6 HE SURVIVES. Same figure as the plate, seated, not redrawn, not doubled.
     The mask is nowhere near him but 0.30 over a pad-crop can still reach.
NOT SCORED: which goblin design he is. The plate is the ratified-then-superseded
adult and the creature ruling is a separate re-render."""

PREDICTED = """S4 IS THE ONE I EXPECT TO ARGUE ABOUT. The four beats where this
method worked composited a SMALL plant -- 4.1% of frame on b13 -- and this one
is 62% of the frame's width, which is the direction the big-leaf attempt
failed in. The defence is that AREA is what the pass cares about and this mask
is 9.84% of the frame against that attempt's eight-times-a-working-mask, but
that is an argument and this sample is the test of it. If the blades come back
flat, the finding is that the ceiling is the object's SPAN and not its area,
which would be new and would close the composite route for foreground subjects.
SECOND: S1, AND IT IS NOT A SAMPLER QUESTION. He may still pull the eye simply
because he is a face and the plant is not. If that is the read, the lever is a
tighter crop -- beat 09 proved this week that crop-and-condition survives i2v at
105% of frame 1's high-frequency energy -- and not another pass.
THIRD: S5. `second plant` and `two plants` are in the negative, and this tree's
negatives have failed to hold position three for three, so they are there for
completeness and not relied on. The erase is what is relied on.
NOT PREDICTED AND WORTH WATCHING: the contact shadow at the stem's base. It is
drawn as an ellipse and 0.30 may resolve it as a hole in the ground."""


def main() -> int:
    write = "--write" in sys.argv
    want = {}
    for name in (INIT, MASK):
        p = os.path.join(REPO, OUT_DIR, name)
        if not os.path.isfile(p):
            print("!! missing %s/%s -- run beat16_sapling_composite.py first"
                  % (OUT_DIR, name))
            return 1
        with open(p, "rb") as fh:
            want[name] = hashlib.sha256(fh.read()).hexdigest()
        print("%-34s sha256 %s" % (name, want[name]))

    fetch = '''#!/usr/bin/env python3
"""Fetch beat 16's WHOLE-SAPLING composite and its mask, refusing on any sha
mismatch. Both files are on origin/main, so these sha256s are verifiable
against the repo by anyone who clones it. They were made on a Mac by
pipeline/beat16_sapling_composite.py, so they are NOT on the box's courier
worktree -- the courier only ever contains what the box produced."""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\%s"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "%s/")
UA = {"User-Agent": "banyan-city-b16-sapcomp/1.0 (albert.numbro@gmail.com)"}
WANT = {
    "%s":
        "%s",
    "%s":
        "%s",
}

os.makedirs(OUT, exist_ok=True)
for name, want in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(RAW + name, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing.\\n   want %%s\\n   have %%s"
                 %% (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%s %%d bytes sha %%s OK" %% (name, len(raw), have), flush=True)
''' % (NEW_DIR_TOKEN, OUT_DIR, INIT, want[INIT], MASK, want[MASK])

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "beat-16 restage lane, 2026-08-20 night",
            "consumer": (
                "BEAT 16'S SLATE IN THE EPISODE 2 CUT -- one of the last two "
                "empty slots, and the beat with no footage candidate of any "
                "kind. Three wordings, one big-leaf composite and a four-plate "
                "field batch have all failed it. This is the first init the "
                "beat has ever had that puts the canon sapling in front of a "
                "seated figure in the episode's own dialect. If it comes out, "
                "the next step is ONE i2v motion sample off it and beat 16 has "
                "a candidate; if it does not, the finding is about the "
                "composite route's ceiling and not about beat 16."),
            "success": (
                "One 832x1216 png in which THE SAPLING IS THE SUBJECT AND THE "
                "SCAVENGER IS DEPTH BEHIND IT, judged by eye at 1:1 and not by "
                "a metric. S1 the eye lands on the plant, not on him; S2 "
                "exactly two leaves on one stem (canon sapling-two-leaves); S3 "
                "they are AVERAGE leaves -- ordinary, no lobes, no lance, no "
                "exaggerated silhouette (canon sapling-cotyledon-shape); S4 the "
                "pass has actually DRAWN them -- line weight and cel shading in "
                "the plate's dialect, not the flat shapes it was handed; S5 ONE "
                "plant in frame, the erased weed does not come back; S6 he "
                "survives unchanged, seated and single. The named degenerate "
                "outcome is the big-leaf one: two pictures that are the same "
                "picture. That is a FAIL and it has a number -- detail inside "
                "the region fell 10.45 to 9.41 when it happened."),
            "why": (
                "$0, ~5 minutes, one seed, and it is the only unspent route on "
                "a beat that has failed at everything else. The recipe is "
                "untouched from a family that has now worked four times "
                "(b19/b15/b03/b13); THE ONE VARIABLE IS THE INIT, which is why "
                "this is a sample and not a batch. The mask is 9.84% of the "
                "frame -- the big-leaf composite that measurably did nothing "
                "asked the same pass to work across eight times a working "
                "mask, and that difference is the whole bet."),
        },
        overrides={
            "payload:fetch_init.py": fetch,
            "payload:prompt.txt": PROMPT,
            "payload:negative.txt": NEGATIVE,
            "key:beat": 16,
            "key:est_minutes": 5,
            "key:script_line": (
                'Beat 16 WHY (1:15-1:22), node.md verbatim: "Close on the '
                "sapling's leaf; the scavenger sits blurred behind it.\" "
                "RESTAGED 2026-08-20 to CLOSE ON THE WHOLE CANON SAPLING with "
                "the scavenger behind it -- the brief's own relation with the "
                "leaf-as-feature clause dropped, which is what canon.yaml "
                "sapling-cotyledon-shape requires. The VO line is UNCHANGED "
                "and is the founder's own 2026-08-19 word to keep: \"He talks "
                "to me because I'm the only thing here that won't file a "
                "report. Buddy, I wish I could. I can't even wave.\""),
            "key:script_authority": (
                "Node 002b-first-citizen, live script `002b-t0-c`, "
                "`approved_by: founder`, `approved_on: 2026-08-03`. The LINE is "
                "untouched; what changes is the STAGING, which is a stage "
                "direction. The restage was logged by the coordinator lane on "
                "2026-08-20 as the option that satisfies BOTH the brief and the "
                "founder's own 08-17 canon ruling; his card "
                "/review/ep2-b16-leaf-0820 stays open and `licence` is still "
                "his to take."),
        },
        retoken=[(PARENT_DIR_TOKEN, NEW_DIR_TOKEN), (PARENT_ID_TOKEN, NEW_ID),
                 ("03-bad-cover-sapcomp-0820.png", INIT),
                 ("03-bad-cover-sapcomp-mask-0820.png", MASK),
                 ("b03-sapcomp", "b16-sapcomp")],
        extra={
            "bar": BAR,
            "failure_predicted_in_advance": PREDICTED,
            "the_one_variable": (
                "THE INIT. Every sampler number is the parent's by copy: 40 "
                "steps, cfg 7.5, strength 0.30, pad-crop 64, blur 8, "
                "animagine-xl-3.1 base weights in the SDXL inpaint pipeline, "
                "seed 20260820, the whole inpaint_fruit.py payload, the env "
                "block, the needs, the dry-run-before-any-model gate and the "
                "no-glob publish. The prompt and negative change because they "
                "describe a different beat, and the fetch changes because it "
                "names different files."),
            "init_provenance": (
                "farm-out/ep2-b16-sapcomp-0820/16-why-sapcomp-0820.png, built "
                "by pipeline/beat16_sapling_composite.py on "
                "farm-out/ep2-b15-mac-plate-0819/"
                "15-good-listener-mac-plate-r1s1.png (sha256 8a9bd14b...4ebe), "
                "the PRE-composite parent of the b15 plate. The weed that plate "
                "carries was erased before anything was drawn -- b19's flood "
                "matte from a dark seed (3,988 px, stable across box sizes "
                "where a threshold-only matte grew 4,292 to 15,904), grown 5 px "
                "to take the lit fringe a threshold cannot see, then a "
                "within-class per-row fill. Two plants in frame would break "
                "`sapling-two-leaves`, and a 0.30 pass PRESERVES a weed rather "
                "than removing one. Full geometry, palette and light "
                "measurements in 16-why-sapcomp-0820.png.geometry.json."),
            "the_mask_is_the_bet": (
                "9.84% of the frame, against a 34% ceiling the tool refuses "
                "above. The drawn plant spans 62% of the frame's width and 59% "
                "of its height while occupying 5.65% of its pixels -- a thin "
                "object can be a close-up's subject without asking the pass to "
                "re-render the picture. The big-leaf composite on "
                "/review/ep2-b16-leaf-0820 failed at eight times a working "
                "mask and measurably changed nothing (detail 10.45 -> 9.41, "
                "same per-pixel movement as the version that worked). This "
                "sample is the test of whether area is what the pass cares "
                "about, or span."),
            "anti_decal_choices": (
                "composite-init-pattern section 3, all three honoured and each "
                "checkable in the geometry sidecar. PROCEDURAL: the plant is "
                "drawn with numpy and PIL, not photographed and not cloned from "
                "nearby pixels. FITTED TO THE OBJECT: the mask is derived from "
                "the drawn silhouette, so the texture edge and the object edge "
                "are the same edge. THE PLATE'S OWN LIGHT: direction MEASURED "
                "from the plate's low-pass luminance gradient over the region "
                "the plant occupies (dx -0.218 dy -0.976), the highlight "
                "crescent placed on the side it names, and the plate's shading "
                "field re-applied multiplicatively over the drawn plant. The "
                "palette is sampled from the WEED BEING DELETED -- b19's law, "
                "the strongest source available, and not a repeat because those "
                "pixels do not survive into the output."),
            "not_done_on_purpose": (
                "No second seed -- one sample before any batch, and the recipe "
                "is unchanged so this sample is about the init. No recipe "
                "change of any kind. No canon edit: sapling-cotyledon-shape is "
                "OBEYED here, not amended, and the `licence` option the founder "
                "was offered is still open. No cut change: beat 16 is a slate "
                "and stays one until he screens something. No motion job filed "
                "yet -- that is the next rung and it is fired only if this "
                "reads as the shot."),
        },
        by="pipeline/derive_b16_sapcomp_0820.py",
    )
    # ---- THE LEAK THE ALLOW-LIST CANNOT CATCH, closed by hand -------------
    # `steps` is structural, so it is carried -- and the parent's `--note`
    # strings are prose full of MEASURED NUMBERS. Beat 03's dry note reads
    # "83000 px, 8.20 percent of the frame, extent x 67..461 y 533..1173" and
    # "that it does not reach his FACE (box x 222..424 y 232..512)". Retoken
    # rewrites ids and filenames and leaves every one of those coordinates
    # standing, so a human checking beat 16's dry PNG would be checking beat
    # 03's boxes and would pass it. derive_spec closes verdict leaks at the top
    # level; a note inside an inherited argv walks straight past it.
    # The numbers below are THIS child's, measured off its own mask.
    NOTES = {
        "dry": (
            "MASK GEOMETRY CHECK. Writes the mask and exits BEFORE a model is "
            "loaded, so a wrong mask costs seconds instead of a GPU fire. The "
            "mask is the union of the ERASED WEED's footprint (dilated 5) and "
            "the DRAWN SAPLING's own footprint plus its contact shadow "
            "(dilated 9) -- 99,533 px, 9.84 percent of the frame, extent "
            "x 151..783 y 302..1199. WHAT TO CHECK ON THE DRY PNG. (1) Above "
            "y=430 the only masked thing is a narrow strip at x 206..241 -- "
            "that is the erased weed, and nothing else up there may be "
            "covered. (2) It touches just 7.0 percent of his head box "
            "(x 310..590 y 194..459) and all of that is at the jaw line, y>=430, "
            "where the drawn leaves pass in front of his chin. THAT OVERLAP IS "
            "BY DESIGN: the plant stands BETWEEN THE CAMERA AND HIM, which is "
            "the whole restage. (3) It must not reach his eyes, brow or the "
            "top of his skull. If it does, the plant is drawn too high and the "
            "fix is --root/--height, not the mask."),
        "s20260820": (
            "ONE SAMPLE, ONE SEED. Every sampler number is the parent job's: 40 "
            "steps, cfg 7.5, strength 0.30, pad-crop 64, blur 8, "
            "animagine-xl-3.1 base weights in the SDXL inpaint pipeline. THE "
            "ONE VARIABLE IS THE INIT. 0.30 runs int(40*0.30) = 12 of 40 "
            "denoising steps from a latent that still carries the drawn "
            "structure, so the high-sigma steps where global layout is decided "
            "never run -- which is why 'finish this structure' succeeds where "
            "'invent this structure' failed, and beat 16 spent three wordings "
            "proving the second half of that. BEAT 16 IS THE FIRST IN THIS "
            "FAMILY WHERE THE COMPOSITED PLANT IS THE SUBJECT rather than set "
            "dressing: b13's was 4.1 percent of frame, this one spans 62 "
            "percent of the width. The bet is that the pass cares about mask "
            "AREA (9.84 percent here) and not about the object's SPAN, and the "
            "big-leaf composite that measurably did nothing is the reason that "
            "is a bet and not an assumption."),
    }
    patched = []
    for step in child.get("steps") or []:
        argv = step.get("argv") or []
        if "--note" in argv and step.get("name") in NOTES:
            argv[argv.index("--note") + 1] = NOTES[step["name"]]
            patched.append(step["name"])
    if sorted(patched) != sorted(NOTES):
        print("!! expected to replace notes on %s, replaced %s -- the parent's "
              "step names changed and a beat-03 note would have shipped."
              % (sorted(NOTES), sorted(patched)))
        return 1
    for step in child.get("steps") or []:
        for tok in step.get("argv") or []:
            if isinstance(tok, str) and ("x 67..461" in tok
                                         or "x 222..424" in tok):
                print("!! a beat-03 coordinate survives in step %r"
                      % step.get("name"))
                return 1
    print("notes replaced on: %s" % ", ".join(patched))

    out = os.path.join(REPO, "pipeline", "jobs", NEW_ID + ".yaml")
    if not write:
        print("\n-- dry run. re-run with --write.")
        return 0
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(derive_spec._dump(child))
    print("wrote pipeline/jobs/%s.yaml" % NEW_ID)

    # THE RETOKEN TRAP, as a guard rather than as a memory: re-read the EMITTED
    # file and check every raw.githubusercontent URL in it against the working
    # tree, AFTER retoken has had its way. ep2-b08-nogoblin-0820 died rc=1 on an
    # invented address that every other check passed.
    dirs = derive_fetch_guard.assert_fetch_urls_resolve(
        out, must_hold=(INIT, MASK))
    print("fetch guard OK: %s" % ", ".join(sorted(dirs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
