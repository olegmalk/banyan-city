#!/usr/bin/env python3
r"""STEP 3 of the sapling LoRA dataset: ONE 0.30 inpaint over each of the
twenty-six composites, in one filing pass.

WHY THIS IS A BATCH AND NOT A SAMPLE, SAID PLAINLY. The standing rule is ONE
SAMPLE BEFORE ANY BATCH, and it is a rule about RECIPE CHANGES: "not one per
session -- one per *recipe change*". NOTHING IN THE RECIPE CHANGES HERE. Every
sampler number is `ep2-b16-sapcomp-r2-0820`'s by copy -- 40 steps, cfg 7.5,
strength 0.30, pad-crop 64, blur 8, animagine-xl-3.1 in the SDXL inpaint
pipeline -- and that recipe is the one that has now finished four composited
plants (b19, b15, b03, b13) plus b16. The variable is the INIT, twenty-six
times, which is exactly what a dataset is. Filing them one at a time would buy
no information and would idle the card between each look.

The honest cost if the family has stopped working: ~26 x 3 GPU-minutes on a card
that is otherwise idle, at $0. The honest cost of filing them singly: the same
GPU time plus twenty-five human round-trips.

WHAT EACH JOB DOES. Fetches its own init and mask from origin/main by sha (they
are committed at farm-out/ep3-saplora-init-0821/, so anyone with a clone
can verify them), runs the mask-geometry dry step BEFORE a model loads, then one
seeded pass, then publishes named files into the courier's farm-out.

THE PROMPT IS PER-FRAME AND IT IS THE PLATE'S OWN SCENE. A 0.30 pass runs
int(40*0.30)=12 of 40 steps from a latent that still carries the drawn
structure, so the prompt's job is to FINISH the plant in the frame's dialect,
not to invent it. Each frame's prompt therefore carries its own scene and light
words -- "golden terraced slopes ... low warm backlight" for u02, "heavy
overcast ... muted colour" for u04 -- because a generic field prompt over a
sunset plate is the pass being told to disagree with the picture it was handed.

NO FIGURE IN ANY PROMPT, and that is the point of the whole plate exercise: the
existing composites carry the scavenger in every frame, and a subject LoRA fed a
figure in every frame learns a figure.

CLIP-77 IS COUNTED BEFORE ANYTHING IS WRITTEN. Ten specs on this same tree were
written, committed, pushed and enqueued on 2026-08-21 with a 135-token payload
and all ten died rc=9 with the card idle. Both payloads of all twenty-six jobs
are counted on animagine's own vocab here, and a term the checkpoint does not
carry is a refusal too.

THE SPECS ON DISK ARE THE AS-RUN SPECS AND A RE-DERIVE WILL DIFFER. All
twenty-six were filed and drained before the retoken ordering below was fixed,
so each committed `pipeline/jobs/ep3-saplora-sNN-0821.yaml` publishes into a
courier directory called `ep2-sap-sNN-r2-0820` -- a name that is wrong about the
episode, the round and the date, and that no check catches because every check
here asks whether a value is THIS CHILD'S, not whether a name is TRUE. Re-running
this deriver emits the corrected name. The committed files are deliberately NOT
regenerated: they are the record of what the card actually did, and the frames
they produced are re-published under their real names by the dataset builder.

ROUND 5 / v2, 2026-08-21. Eleven more rows (s27..s37) were added to B.ROWS on
four NON-DAYLIT plates -- night, storm shaft, rain, after-rain -- because every
one of v1's eleven plates is lit by day and a subject LoRA whose every frame
shares a time of day learns the time of day into the trigger. Nothing about the
recipe moves for them either: same 40 steps, cfg 7.5, strength 0.30, pad-crop
64, blur 8, same seed, same negative shape. The only new thing in this file is
the no-clobber guard at the write, and it exists because extending B.ROWS is
exactly the move that would otherwise have rewritten the drained twenty-six.

ROUND 6 / v3, 2026-08-21. Seven more rows (s38..s44) on TWO more non-daylit
plates -- w03 (moonlight through broken cloud) and w02 (a low sun behind thin
cloud) -- from a four-cell word probe whose other two cells are judged and
rejected in plates-0821.yaml. Still no recipe change: the same 40 steps, cfg
7.5, strength 0.30, pad-crop 64, blur 8, the same seed. The tiers are picked off
the manifest's thin end (l and xl) rather than spread evenly, and the
no-clobber guard below is what makes extending B.ROWS a safe move for the
second time.

  python3 pipeline/derive_sapling_lora_naturalize_0821.py            # dry
  python3 pipeline/derive_sapling_lora_naturalize_0821.py --write
  python3 pipeline/derive_sapling_lora_naturalize_0821.py --write --regen
"""

from __future__ import annotations

import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec            # noqa: E402
import derive_fetch_guard     # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77  # noqa: E402
import build_sapling_lora_composites_0821 as B             # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b16-sapcomp-r2-0820.yaml"
PARENT_DIRTOK = "b16sapcomp-r2-0820"
PARENT_ID = "ep2-b16-sapcomp-r2-0820"
PARENT_INIT = "16-why-sapcomp-0820.png"
PARENT_MASK = "16-why-sapcomp-mask-0820.png"
PARENT_OUTTOK = "b16-sapcomp"

SRC_DIR = "farm-out/ep3-saplora-init-0821"
SEED = 20260820   # the parent job's, unchanged -- see the_one_variable

# The plant clause is IDENTICAL in all twenty-six prompts. It is the canon
# description and it is the only thing the LoRA is being taught, so it is the
# one thing that must not vary with the scene.
PLANT = ("a young sapling with exactly two wide oval leaves with soft round "
         "tips on one thin bare stem, rooted in the ground")

# per tier, the scale words. Short, because CLIP has 77 tokens and the scene
# clause has to fit too.
TIER_WORDS = {
    "s":  "a tiny sprout, small in a wide frame",
    "m":  "small, at middle distance",
    "l":  "standing clear of the grass, mid frame",
    "xl": "close to the camera, large in frame",
}

# 74 tokens on animagine's vocab, counted below before anything is written.
# The first draft was 82 and assert_under_clip77 refused it: `leaflets`,
# `palmate`, `plant girl`, `alraune` and `lowres` came out, in that order,
# because they are the terms furthest from a failure this batch has ever seen.
# The count bans that stayed are the ones canon `sapling-two-leaves` rests on.
NEGATIVE = ("three leaves, four leaves, many leaves, extra stalk, branching "
            "stem, pointed lance leaves, lobed leaves, bud, flower, fruit, "
            "large tree, thick branch, second plant, two plants, 1boy, people, "
            "goblin, text, photorealism, 3d render, low quality, worst quality, "
            "blurry")


def prompt_for(fid, pk, tier):
    s = B.SCENES[pk]
    return "%s, %s, %s, %s, no humans, detailed cinematic anime, masterpiece, " \
           "best quality, very aesthetic" % (PLANT, TIER_WORDS[tier],
                                             s["scene"], s["light"])


BAR = """JUDGED BY EYE AT CONTACT-SHEET LEVEL, AS A DATASET AND NOT AS A SHOT.
This frame is never cut into anything; its only consumer is the sapling LoRA's
training set, so the bars are the ones a training frame has to clear.
  D1 EXACTLY TWO LEAVES ON ONE STEM. Canon `sapling-two-leaves`. Three is a
     delete, so is one. The init has two by construction, so a three here means
     the 0.30 pass invented one and the finding is about the pass.
  D2 AVERAGE LEAVES. Canon `sapling-cotyledon-shape` -- ordinary, plain, no
     lobes, no lance, no exaggerated silhouette.
  D3 NO FIGURE, NO CREATURE, ANYWHERE IN FRAME. A frame carrying one is
     DELETED, not cropped. This tree's negatives have failed to hold position
     five times and the plates exist precisely because the ~23 existing
     composites all carry the scavenger.
  D4 THE PLANT IS DRAWN, NOT PASTED. Line weight and cel shading in the plate's
     dialect. The named degenerate outcome has a number: on the b16 big-leaf
     attempt detail inside the region fell 10.45 -> 9.41 and the two pictures
     were the same picture. If nothing visibly happened to the blades, the
     frame is a reject and the finding is about mask size.
  D5 THE SCENE SURVIVES. The pass may not repaint the plate around the mask --
     the whole point of eleven plates is eleven backgrounds.
  D6 ONE PLANT. No second sapling grown out of the grass beside it."""

PREDICTED = """FIRST AND MOST LIKELY, AND IT IS A DATASET RISK RATHER THAN A
PICTURE RISK: the pass works and every frame is fine, and the set is still
short of the gate on the LEAF-COUNT axis, because all twenty-six have two
leaves. That is stated in the manifest rather than hidden -- there is no tool
here that ADDS a leaf, only one that removes them -- and it is the honest
reading of "leaf count stays a caption variable": the token is present and
explicit in every caption so it can never fuse into the trigger, but its VALUE
never changes in v1.
SECOND: D3, the figure. Five failures in a row on this tree's negatives say the
ban does not hold, and `1boy` and `goblin` are in the negative here for
completeness only. The defence is that the mask is 1.3-11% of the frame and a
figure would have to be painted inside it.
THIRD, AND IT IS THE ONE THAT WOULD CLOSE THE ROUTE: the tiny rows. s01's mask
is 1.28% of the frame and the plant is 150 px tall. Every previous success in
this family was 4-10%; a mask this small may be below the pad-crop's useful
resolution and come back untouched. If the small tier fails and the large tier
passes, the finding is a FLOOR on this method and the dataset's scale axis
narrows to what survives."""


def main() -> int:
    write = "--write" in sys.argv
    n_ok = 0
    filed = []
    for fid, pk, tier, root, height, tilt, lf, ls in B.ROWS:
        new_id = "ep3-saplora-%s-0821" % fid
        dirtok = "saplora-%s-0821" % fid
        init = "sap-%s-%s-0821.png" % (fid, pk)
        mask = "sap-%s-%s-mask-0821.png" % (fid, pk)
        want = {}
        for name in (init, mask):
            p = os.path.join(REPO, SRC_DIR, name)
            if not os.path.isfile(p):
                print("!! missing %s/%s -- run "
                      "build_sapling_lora_composites_0821.py --write first"
                      % (SRC_DIR, name))
                return 1
            with open(p, "rb") as fh:
                want[name] = hashlib.sha256(fh.read()).hexdigest()

        prompt = prompt_for(fid, pk, tier)
        np_ = assert_under_clip77("%s prompt" % new_id, prompt)
        nn_ = assert_under_clip77("%s negative" % new_id, NEGATIVE)

        fetch = '''#!/usr/bin/env python3
"""Fetch this dataset frame's composited init and its mask, refusing on any sha
mismatch. Both are on origin/main under farm-out/ep3-saplora-init-0821/, so
these sha256s are verifiable against the repo by anyone who clones it. They
were drawn on a Mac by pipeline/beat16_sapling_composite.py, so they are NOT on
the box's courier worktree -- the courier only holds what the box produced."""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\%s"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "%s/")
UA = {"User-Agent": "banyan-city-saplora/1.0 (albert.numbro@gmail.com)"}
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
''' % (dirtok, SRC_DIR, init, want[init], mask, want[mask])

        scene = B.SCENES[pk]
        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "sapling-dataset lane, 2026-08-21",
                "consumer": (
                    "THE SAPLING LoRA'S TRAINING SET and nothing else -- "
                    "pipeline/lora/README.md, which gates it at >=20 "
                    "composited saplings across distinct scenes, scales and "
                    "lighting. This is frame %s of %d, drawn on plate %s (%s). "
                    "It is not a beat, it does not enter a cut, and it is not "
                    "a candidate for one. DECISIONS.md item 18 ('never train "
                    "on the output') is open and unresolved; this builds the "
                    "dataset the question is ABOUT and decides nothing."
                    % (fid, len(B.ROWS), pk, scene["scene"])),
                "success": (
                    "One 832x1216 png of the canon two-leaf sapling STANDING IN "
                    "%s under %s, with the plant NATURALIZED into the plate's "
                    "cel dialect -- line weight and shading on the blades, not "
                    "the flat drawn shapes the init handed it -- and NO FIGURE "
                    "AND NO CREATURE anywhere in the frame. Exactly two leaves "
                    "on one stem, one plant only, and the background unchanged "
                    "outside the mask. Judged at contact-sheet level with its "
                    "twenty-five siblings, as a training frame and not as a "
                    "shot. A frame with a figure in it is DELETED under bar D3."
                    % (scene["scene"], scene["light"])),
                "why": (
                    "$0 and ~3 minutes on a card that is otherwise idle. The "
                    "recipe is unchanged from a family that has finished five "
                    "composited plants; the ONE variable is the init, and "
                    "twenty-six inits is what a dataset is. The plant is %d px "
                    "tall rooted at %s with leaves %.2f of the stem, so the "
                    "mask is small and local and the pass is being asked to "
                    "finish a structure rather than invent one."
                    % (height, root, lf)),
            },
            overrides={
                "argv:--init-sha256": want[init],
                "payload:fetch_init.py": fetch,
                "payload:prompt.txt": prompt,
                "payload:negative.txt": NEGATIVE,
                "key:node": "001-capability-inventory",
                "key:beat": 0,
                "key:est_minutes": 3,
                "key:priority": 55,
                "key:script_line": (
                    "NONE. This frame illustrates no beat and no line. It is a "
                    "LoRA training frame; the beat/script fields exist because "
                    "the queue schema wants them, and inheriting beat 16's "
                    "line here would be a false claim about what this picture "
                    "is for."),
                "key:script_authority": (
                    "NOT A SCRIPTED SHOT, so §6 narrative approval is not the "
                    "gate that applies and is not being claimed. The node is "
                    "named only because the queue's approval check reads a "
                    "leaf; `001-capability-inventory` is live and "
                    "founder-approved, and this job renders no line from it. "
                    "What governs this frame is pipeline/lora/README.md's "
                    "dataset gate and the canon rulings `sapling-two-leaves` "
                    "(2026-08-16) and `sapling-cotyledon-shape` (2026-08-17)."),
            },
            # ORDER IS LOAD-BEARING AND THE FIRST FILING GOT IT WRONG.
            # derive_spec applies these pairs IN ORDER and appends its own
            # (parent_id -> new_id) LAST, so a SHORTER pattern that is a
            # substring of the parent id runs first and eats it. `b16-sapcomp`
            # is a substring of `ep2-b16-sapcomp-r2-0820`, so the outtok rule
            # rewrote the id into `ep2-sap-sNN-r2-0820` before the id rule could
            # see it -- and that string is a publish DIRECTORY NAME, so all
            # twenty-six jobs published into courier dirs claiming episode 2,
            # round 2, and the date 0820. Wrong on three counts and none of them
            # caught by a check, because every check here asks whether a value
            # is THIS CHILD'S, not whether a name is true.
            # THE PARENT ID GOES FIRST. Longest-first is the general rule; the
            # id is the longest string any of these can hide inside.
            retoken=[(PARENT_ID, new_id),
                     (PARENT_DIRTOK, dirtok),
                     (PARENT_INIT, init),
                     (PARENT_MASK, mask),
                     (PARENT_OUTTOK, "sap-%s" % fid)],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "the_one_variable": (
                    "THE INIT. Every sampler number is %s's by copy: 40 steps, "
                    "cfg 7.5, strength 0.30, pad-crop 64, blur 8, "
                    "animagine-xl-3.1 base weights in the SDXL inpaint "
                    "pipeline, the whole inpaint_fruit.py payload, the env "
                    "block, the needs, the dry-run-before-any-model gate and "
                    "the no-glob publish. The SEED moves to %d for the whole "
                    "batch so no frame shares a seed with the beat-16 sample "
                    "it descends from. The prompt and negative change because "
                    "they describe a different picture." % (PARENT_ID, SEED)),
                "init_provenance": (
                    "%s/%s, drawn by pipeline/beat16_sapling_composite.py via "
                    "pipeline/build_sapling_lora_composites_0821.py row %s on "
                    "plate farm-out/ep3-sapling-dataset-0821/plates/%s. Root "
                    "%s, stem %d px, tilt %.1f deg, leaf-frac %.2f, leaf-spread "
                    "%.1f deg. No plant was erased -- the plate is plant-free "
                    "by construction, which is the whole reason the plate round "
                    "was run. Palette sampled from the plate's own greens, "
                    "light direction measured from its low-pass luminance "
                    "gradient; full numbers in the .geometry.json beside it."
                    % (SRC_DIR, init, fid, scene["plate"], root, height, tilt,
                       lf, ls)),
                "dataset_row": (
                    "frame_id %s | plate %s | tier %s | scene: %s | light: %s | "
                    "root %s | stem_px %d | leaf_frac %.2f"
                    % (fid, pk, tier, scene["scene"], scene["light"], root,
                       height, lf)),
                "clip_budget": (
                    "prompt %d tokens, negative %d tokens, both counted on "
                    "animagine's own vocab by "
                    "derive_sapling_field_0821.assert_under_clip77 BEFORE this "
                    "file was written. Ten specs on this tree died rc=9 at 135 "
                    "tokens with the card idle on 2026-08-21; overflow is "
                    "SILENT and drops the TAIL, so a long negative does not "
                    "ban harder, it bans nothing." % (np_, nn_)),
                "not_done_on_purpose": (
                    "No recipe change of any kind. No second seed per frame -- "
                    "the variety this dataset needs is across SCENES, not "
                    "across seeds of one scene. No leaf-count variation: "
                    "beat16_sapling_composite draws the canon two, "
                    "leaf_count_composite only REMOVES leaves from a plate that "
                    "has too many, and inventing a third here would break "
                    "`sapling-two-leaves` to satisfy a dataset axis. No "
                    "training is started, no trainer is installed, and "
                    "DECISIONS.md item 18 is left open for the founder."),
            },
            by="pipeline/derive_sapling_lora_naturalize_0821.py",
        )

        # ---- THE PARENT'S NOTES ARE BEAT 16'S PROSE, FULL OF BEAT 16'S
        # ---- MEASURED COORDINATES, and retoken rewrites ids and filenames and
        # ---- leaves every number standing. A human checking this frame's dry
        # ---- PNG would be checking the b15 plate's head box and would pass it.
        # The parent's seeded step is named for ITS seed (`s20260820`), and an
        # argv override does not rename a step. Find it rather than assume it:
        # a note keyed to a name that no longer exists means beat 16's own
        # coordinates ship on this frame, which is what the check below refuses.
        seeded = [st.get("name") for st in (child.get("steps") or [])
                  if re.fullmatch(r"s\d{8}", str(st.get("name") or ""))]
        if len(seeded) != 1:
            print("!! %s: expected exactly one seeded step, found %s"
                  % (new_id, seeded))
            return 1
        SEED_STEP = seeded[0]
        notes = {
            "dry": (
                "MASK GEOMETRY CHECK. Writes the mask and exits BEFORE a model "
                "is loaded, so a wrong mask costs seconds instead of a GPU "
                "fire. THERE IS NO FIGURE AND NO ERASED PLANT IN THIS FRAME -- "
                "the plate is plant-free and person-free by construction -- so "
                "the mask is exactly the drawn sapling plus its contact shadow, "
                "dilated 9. WHAT TO CHECK: (1) it is ONE connected blob shaped "
                "like a stem with two leaves, not two blobs and not a "
                "rectangle; (2) it does not reach the top of the frame, which "
                "would mean the plant was drawn taller than the picture; (3) "
                "nothing is masked below the root at y=%d except the contact "
                "ellipse. If any of those is wrong the fix is --root/--height "
                "in build_sapling_lora_composites_0821.py, not the mask."
                % root[1]),
            SEED_STEP: (
                "ONE PASS, ONE SEED, TWENTY-SIX SIBLINGS. 0.30 runs "
                "int(40*0.30) = 12 of 40 denoising steps from a latent that "
                "still carries the drawn structure, so the high-sigma steps "
                "where global layout is decided never run -- which is why "
                "'finish this structure' succeeds where 'invent this "
                "structure' failed, and the sapling's wording ladders are "
                "CLOSED on the second half of that (0 of 16 frames with two "
                "leaves from the strongest wording available). This frame is "
                "row %s: plate %s, %s, stem %d px, mask small and local. It is "
                "a LoRA training frame and is judged against its siblings on a "
                "contact sheet, not as a shot."
                % (fid, pk, TIER_WORDS[tier], height)),
        }
        patched = []
        for step in child.get("steps") or []:
            argv = step.get("argv") or []
            if "--note" in argv and step.get("name") in notes:
                argv[argv.index("--note") + 1] = notes[step["name"]]
                patched.append(step["name"])
        if sorted(patched) != sorted(notes):
            print("!! %s: expected to replace notes on %s, replaced %s"
                  % (new_id, sorted(notes), sorted(patched)))
            return 1
        for step in child.get("steps") or []:
            for tok in step.get("argv") or []:
                if isinstance(tok, str) and ("x 151..783" in tok
                                             or "x 310..590" in tok
                                             or "head box" in tok):
                    print("!! %s: a beat-16 coordinate survives in step %r"
                          % (new_id, step.get("name")))
                    return 1

        # hash sweep + the named init assertion, both b16's, both kept
        mine = set(want.values())
        for step in child.get("steps") or []:
            for tok in step.get("argv") or []:
                if not isinstance(tok, str):
                    continue
                for h in re.findall(r"\b[0-9a-f]{64}\b", tok):
                    if h not in mine:
                        print("!! %s: step %r carries foreign sha %s..."
                              % (new_id, step.get("name"), h[:12]))
                        return 1
        seen = 0
        for step in child.get("steps") or []:
            argv = step.get("argv") or []
            if "--init" not in argv or "--init-sha256" not in argv:
                continue
            # NOT os.path.basename: these are WINDOWS paths on a Mac.
            named = str(argv[argv.index("--init") + 1]
                        ).replace("\\", "/").rsplit("/", 1)[-1]
            claimed = str(argv[argv.index("--init-sha256") + 1])
            if named != init:
                print("!! %s: step %r conditions on %r, not %r"
                      % (new_id, step.get("name"), named, init))
                return 1
            if claimed != want[init]:
                print("!! %s: step %r asserts %s... but %s hashes %s..."
                      % (new_id, step.get("name"), claimed[:12], init,
                         want[init][:12]))
                return 1
            seen += 1
        if not seen:
            print("!! %s: no step carries --init with --init-sha256" % new_id)
            return 1

        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        # A SPEC ON DISK IS THE AS-RUN RECORD AND IS NOT OVERWRITTEN. The
        # docstring above says the committed twenty-six are "the record of what
        # the card actually did"; that was prose, and prose is not a guard. It
        # became one when round 5 added rows to B.ROWS: a plain --write over the
        # extended table would have silently rewritten all twenty-six drained
        # specs (with the retoken fix applied, so their publish directory names
        # would no longer match the directories the box actually wrote) to file
        # eleven new ones. Now the run files only what does not exist, and
        # --regen is the explicit way to say you mean it.
        if write and os.path.exists(out) and "--regen" not in sys.argv:
            print("%-22s %-4s KEPT AS-RUN (spec exists; --regen to rewrite)"
                  % (new_id, pk))
            n_ok += 1
            continue
        if write:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(derive_spec._dump(child))
            derive_fetch_guard.assert_fetch_urls_resolve(
                out, must_hold=(init, mask), log=lambda *a, **k: None)
            filed.append(new_id)
        n_ok += 1
        print("%-22s %-4s p%-3d n%-3d init %s..." % (new_id, pk, np_, nn_,
                                                     want[init][:10]))

    print("\n%d/%d specs derived, clip77 counted, hash-swept, "
          "init-asserted" % (n_ok, len(B.ROWS)))
    if write:
        print("wrote %d specs into pipeline/jobs/" % len(filed))
    else:
        print("-- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
