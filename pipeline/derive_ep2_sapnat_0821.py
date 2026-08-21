#!/usr/bin/env python3
r"""Derive the three PLATE-SIDE naturalize jobs for beats 02, 03 and 20.

    python3 pipeline/derive_ep2_sapnat_0821.py            # dry run, writes nothing
    python3 pipeline/derive_ep2_sapnat_0821.py --write
    python3 pipeline/derive_ep2_sapnat_0821.py --write --force

THE LAW THESE JOBS EXIST TO SATISFY, AND IT WAS MEASURED BEFORE IT WAS ACTED ON
--------------------------------------------------------------------------
The canon-motion wave of 2026-08-21 filed seven i2v jobs on the founder-image
canon plates and scored every one of them by eye. The four that failed failed
the SAME way, and each verdict says so in its own spec, in its own words:

  b02  "between f024 and f048 the camera pulls back until he is a few percent
        of the frame height, and by f104 he is a speck at bottom right of a
        wide shot dominated by a large bare tree that is in no plate."
  b03  "the camera pulls back from ~f072 and his height roughly halves by f104.
        No trunk is ever drawn, so the beat's cover does not exist."
  b07  "the camera also pulls back at f024 to fit the second figure."
  b20  "a branch enters at top right from ~f048 and he never turns to it."

The three that PASSED -- 04, 08 and 13 -- each ask only for motion the plate
already has a body for. Nothing else separates the two groups: same recipe,
same size, same guidance, same sampler, same frame count, same seed policy.

So the generalisation is A PROMPT THAT NAMES AN OBJECT ABSENT FROM THE INIT
MAKES THE MODEL BUILD THE OBJECT AND RE-FRAME THE SHOT TO FIT IT, and the fix
is plate-side rather than a sixth rewording. b02 and b03 need the scripted thin
sapling trunk IN the plate; b20 needs the branch beside him. That is what these
three jobs draw. b07 needs a second FIGURE and is a different route (a two-
figure skeleton), filed separately -- it is not in this deriver.

WHAT IS NOT NEW HERE: NOT ONE SAMPLER NUMBER
--------------------------------------------------------------------------
The recipe is the b16 whole-sapling composite rung carried by copy: 40 steps,
cfg 7.5, strength 0.30, pad-crop 64, blur 8, seed 20260820, the whole
inpaint_fruit.py payload, the env block, the needs, the dry-run-before-any-
model mask gate, and the no-glob publish. 0.30 runs int(40*0.30) = 12 of 40
denoising steps from a latent that still carries the drawn structure, so the
high-sigma steps where global layout is decided never run. That is the whole
reason this pass can draw a pasted shape into the plate's dialect WITHOUT
moving it -- it finishes a structure instead of inventing one.

WHY THREE AT ONCE IS NOT A BATCH, AND THE EVIDENCE FOR IT IS ON DISK
--------------------------------------------------------------------------
The one-sample rule bites on a RECIPE CHANGE, and there is none here. This
exact pass has already run on this exact material: farm-out/ep2-b03-sapcomp-
0820/ and farm-out/ep2-b13-sapcomp-0820/ each hold the composite that went in
and the naturalised png that came out, at this seed and these numbers. Read
side by side they show the pass doing precisely its job -- the flat pasted
leaves come back drawn, with cel shading and the plate's own line weight, and
the plant has not moved. Those two outputs are the sample, they were judged by
eye before this file was written, and what changes here is THE INIT: three
beats, three different plates, three independent questions. Scaling an
UNAPPROVED result is what the rule forbids; this is a proven rung applied to
new inits, which is the same argument the canon-motion tranche made for seven.

WHAT A LANE MUST STILL DO AFTER THIS RUNS
--------------------------------------------------------------------------
Open the three pngs. If the plant reads drawn and has not moved, re-derive the
beat's motion spec off the FIXED plate -- and only then may the motion prompt
name the trunk or the branch, because by then the init contains it.
"""
import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402
import derive_fetch_guard                                     # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77     # noqa: E402

PARENT = "pipeline/jobs/ep2-b16-sapcomp-r2-0820.yaml"
PARENT_ID = "ep2-b16-sapcomp-r2-0820"
PARENT_PUBDIR = "ep2-b16-sapcomp-0820"
PARENT_DIRTOK = "b16sapcomp-r2-0820"
PARENT_INIT = "16-why-sapcomp-0820.png"
PARENT_MASK = "16-why-sapcomp-mask-0820.png"
PARENT_OUTTOK = "b16-sapcomp"
SEED = 20260820

# THE PARENT'S NEGATIVE IS 84 CLIP TOKENS AND THE CEILING IS 77, measured by
# assert_under_clip77 when this deriver first ran. That is not a style note: the
# overflow is SILENT and drops FROM THE TAIL, so the b16 rung as filed banned
# nothing from "chibi" onward -- `standing, text, photorealism, 3d render, low
# quality` never reached the sampler. Carrying it verbatim would have carried a
# dead tail into three more specs. It is trimmed to 60 tokens here by dropping
# only terms another term already covers: `four leaves`/`leaflets` (under `many
# leaves`), `multi-node weed` and `palmate` (under `branching stem`/`lobed
# leaves`), `two plants` (under `second plant`), and `2boys`/`chibi`/`standing`,
# which describe the FIGURE -- and the mask never reaches him, by P4.
NEGATIVE_BASE = (
    "three leaves, many leaves, extra stalk, branching stem, pointed lance "
    "leaves, lobed leaves, bud, flower, fruit, large tree, thick branch, "
    "forest, second plant, plant girl, alraune, child, text, photorealism, "
    "3d render, low quality")
# Beat 20 holds the canon PURPLE fig in both hands, in this same plate. The
# pad-crop around the mask can reach it, and "fruit" in the negative is then
# pointed at the one object the beat is about. Struck for that beat only.
NEGATIVE_B20 = NEGATIVE_BASE.replace("bud, flower, fruit, large tree",
                                     "bud, flower, large tree")

PLANT = ("a young sapling with exactly two wide oval leaves with soft round "
         "tips on one thin bare stem, rooted in the grass")


def prompt_for(behind: str) -> str:
    return ("%s in the foreground, with one small green goblin %s behind it, "
            "solo, sunny grassy field, detailed cinematic anime, masterpiece, "
            "best quality, very aesthetic" % (PLANT, behind))


ROWS = [
    {
        "beat": 2,
        "behind": "running through tall grass",
        "negative": NEGATIVE_BASE,
        "object": "the thin sapling trunk he dives behind",
        "script_line": (
            "THE SPRINT -- 'sprints into frame, skids, and dives behind the "
            "sapling's thin trunk'. He is running from the guards and has not "
            "seen the sapling yet. This is the most frightened he is in the "
            "episode."),
        "staging": (
            "The stem stands in the foreground left of centre, crossing him "
            "from thigh to shoulder, with the two leaves at his forearm. That "
            "is the object the script gives him to dive BEHIND, so it belongs "
            "in front of him and at his own scale -- a thin trunk, not a tree. "
            "The motion verdict's 'large bare tree that is in no plate' is "
            "exactly what this replaces."),
        "cause": (
            "the action names a thin sapling trunk, the canon b02 plate "
            "contains none, and LTX built the tree and re-framed the shot to "
            "fit it"),
    },
    {
        "beat": 3,
        "behind": "crouching low in tall grass",
        "negative": NEGATIVE_BASE,
        "object": "the trunk that hides roughly one-sixth of him",
        "script_line": (
            "BAD COVER -- 'crouches behind a trunk that hides roughly one-"
            "sixth of him'. The comedy is that he believes it is working, so "
            "the face is furtive rather than terrified -- held breath, not a "
            "scream."),
        "staging": (
            "The stem runs up the centre of the frame across his chest. THAT "
            "IS THE JOKE AND NOT A COMPOSITION FAULT: the script asks for "
            "cover that hides about one-sixth of him, so a thin stem drawn "
            "over his middle is the beat. A trunk wide enough to actually "
            "hide him would be the wrong picture."),
        "cause": (
            "the action names a trunk the plate does not contain -- same root "
            "cause as beat 02, and the b03 verdict says so"),
    },
    {
        "beat": 20,
        "behind": "squatting in tall grass",
        "negative": NEGATIVE_B20,
        "object": "the sapling's thinnest branch beside him",
        "script_line": (
            "EVIDENCE -- 'crouches back down, picks the fig up with both "
            "hands, and looks from it to the sapling's thinnest branch beside "
            "him'. Line: '...Did you just ANSWER me?' Awe. The episode's turn."),
        "staging": (
            "The stem stands clear of him at frame right, its two leaves at "
            "about his eye line -- 'the branch beside him', a thing he can "
            "turn his head to. It does not cross his body, because the beat "
            "needs a LOOK from the fig to the branch and both have to be "
            "separately findable. THE FIG WAS ALSO RECOLOURED TO CANON PURPLE "
            "in this composite by pipeline/beat20_fig_recolor.py: the motion "
            "verdict caught it yellow-green where canon has it purple, 'the "
            "same fault in a new colour, carried by the plate'."),
        "cause": (
            "the branch the action names is absent, so it entered on its own "
            "at top right from ~f048 and the frame drifted to accommodate it"),
    },
]


def new_id(beat: int) -> str:
    return "ep2-b%02d-sapnat-0821" % beat


def sha256_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def paths_for(beat: int) -> dict:
    d = "farm-out/ep2-b%02d-sapnat-0821" % beat
    init = "b%02d-sapnat-in-0821.png" % beat
    mask = "b%02d-sapnat-in-mask-0821.png" % beat
    return {"dir": d, "init": init, "mask": mask,
            "init_abs": os.path.join(REPO, d, init),
            "mask_abs": os.path.join(REPO, d, mask)}


FETCH = '''#!/usr/bin/env python3
"""Fetch beat {beat:02d}'s canon-plate composite and its mask, refusing on any sha
mismatch. Both files are on origin/main, so these sha256s are verifiable
against the repo by anyone who clones it. They were made on a Mac, so they are
NOT on the box's courier worktree -- the courier only ever contains what the
box produced."""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\b{beat:02d}sapnat-0821"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "farm-out/ep2-b{beat:02d}-sapnat-0821/")
UA = {{"User-Agent": "banyan-city-b{beat:02d}-sapnat/1.0 (albert.numbro@gmail.com)"}}
WANT = {{
    "{init}":
        "{init_sha}",
    "{mask}":
        "{mask_sha}",
}}

os.makedirs(OUT, exist_ok=True)
for name, want in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(RAW + name, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %s -- refusing.\\n   want %s\\n   have %s"
                 % (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %s %d bytes sha %s OK" % (name, len(raw), have), flush=True)
'''


BAR = """JUDGED BY EYE AT 1:1, AND THE QUESTION IS NARROW.

  P1  THE OBJECT IS DRAWN, NOT PASTED. The two leaves and the stem carry cel
      shading and the plate's own ink line weight. The flat vector fill and
      the hard cut edge the compositor left are gone.
  P2  IT HAS NOT MOVED. Stem root, height and leaf tips sit where the
      compositor put them, within a few px. 0.30 finishes a structure; if the
      plant has relocated, the strength was wrong and the number is the fix.
  P3  EXACTLY TWO LEAVES ON ONE STEM. Canon sapling-two-leaves. Three leaves,
      leaflets, a branching stem or a second plant is a FAIL.
  P4  HE SURVIVES UNCHANGED. Face, ears, skin colour, wardrobe and pose are
      the canon plate's, untouched. The mask is local and the pass must not
      have reached him.
  P5  IT SITS IN THE GRASS. Contact where it meets the ground, no floating
      stem, no halo of untouched pixels around the masked region.

A FAIL on P2 or P4 kills the plate. A FAIL on P1 alone is a strength question
and is worth one more round; a FAIL on P3 is a wording question. Two rounds is
the budget, and after that the beat goes to the founder as it stands."""


def why_for(row: dict) -> str:
    return (
        "BEAT %02d'S MOTION FAILED PLATE-SIDE, AND THIS DRAWS THE MISSING "
        "OBJECT INTO THE PLATE INSTEAD OF REWORDING THE PROMPT AT IT.\n\n"
        "The canon-motion verdict for this beat reads, in its own spec: %s. "
        "That is one instance of a law the wave measured four times -- a "
        "prompt naming an object ABSENT from the init makes the model build "
        "the object and pull the camera back hunting for it, while the three "
        "beats whose prompts ask only for motion the plate has a body for "
        "(04, 08, 13) all held their frame. So the lever is the init.\n\n"
        "WHAT THIS JOB DOES: takes the canon w2 plate for beat %02d with %s "
        "already composited in by hand, and runs the b16 rung's 0.30 masked "
        "i2i over the drawn region ONLY, so the object comes back drawn in "
        "the plate's dialect without moving. %s\n\n"
        "WHAT IT DOES NOT DO: it does not touch the cut, it does not re-render "
        "any motion, and it does not change a single sampler number. The "
        "motion re-derive is a separate spec that may only be filed once a "
        "human has looked at this png."
        % (row["beat"], row["cause"], row["beat"], row["object"],
           row["staging"]))


def consumer_for(row: dict) -> str:
    return (
        "THE INIT FOR BEAT %02d'S RE-DERIVED MOTION SPEC, and nothing else "
        "until then. Named consumer: the canon-motion lane, which cannot file "
        "beat %02d's next i2v rung until a plate exists that contains %s -- "
        "because the wave proved that naming it in the prompt alone re-frames "
        "the shot. Nothing in review/ep2-ship-0821 reads this file, and no cut "
        "changes because it landed."
        % (row["beat"], row["beat"], row["object"]))


def success_for(row: dict) -> str:
    return (
        "ONE 832x1216 png in which %s IS DRAWN INTO THE PLATE AND HAS NOT "
        "MOVED, judged by eye at 1:1 and not by a metric. P1 the stem and both "
        "leaves carry cel shading and the plate's ink line weight, not the "
        "compositor's flat fill; P2 root, height and leaf tips are within a "
        "few px of where they were composited; P3 exactly two leaves on one "
        "stem; P4 the goblin's face, ears, skin colour, wardrobe and pose are "
        "the canon plate's, untouched -- the mask is local and the pass must "
        "not reach him; P5 the stem makes contact with the grass, with no "
        "floating base and no halo of untouched pixels at the mask edge. The "
        "named degenerate outcome is a RELOCATED or REGROWN plant: if 0.30 has "
        "moved it or given it a third leaf, this plate is a FAIL and the fix "
        "is the number or the wording, not another seed."
        % row["object"])


def note_for(row: dict) -> str:
    return (
        "ATTACHED TO BOTH THE DRY STEP AND THE RENDER STEP, and true of each. "
        "ON THE DRY STEP it is a MASK GEOMETRY CHECK: it writes the mask and "
        "exits BEFORE a model is loaded, so a wrong mask costs seconds instead "
        "of a GPU fire. WHAT TO CHECK: (1) one connected blob shaped like a "
        "stem with two leaves, not two blobs and not a rectangle; (2) it does "
        "not reach the top of the frame; (3) it does not cover the goblin's "
        "head or hands -- if it does, the pass will redraw HIM, which is a P4 "
        "fail by construction. ON THE RENDER STEP: one pass, one seed. 0.30 "
        "runs 12 of 40 steps from a latent that still holds the drawn "
        "structure, so the layout steps never run and the pass FINISHES the "
        "shape rather than inventing one. This is beat %02d, whose motion take "
        "failed because %s."
        % (row["beat"], row["cause"]))


def spec_for(row: dict, force: bool):
    beat = row["beat"]
    nid = new_id(beat)
    p = paths_for(beat)
    for f in (p["init_abs"], p["mask_abs"]):
        if not os.path.isfile(f):
            raise SystemExit("!! missing composite input %s" % f)
    init_sha, mask_sha = sha256_of(p["init_abs"]), sha256_of(p["mask_abs"])
    prompt = prompt_for(row["behind"])
    assert_under_clip77("b%02d prompt" % beat, prompt)
    assert_under_clip77("b%02d negative" % beat, row["negative"])

    dirtok = "b%02dsapnat-0821" % beat
    outtok = "b%02d-sapnat" % beat
    # LONGEST FIRST. `b16-sapcomp` is a substring of `ep2-b16-sapcomp-0820`, and
    # the parent id is appended last by derive_spec, so both fuller forms have
    # to be spent before the bare token gets a turn.
    retoken = [
        (PARENT_ID, nid),
        ("ep2-" + PARENT_PUBDIR.split("ep2-")[1], "ep2-b%02d-sapnat-0821" % beat),
        (PARENT_MASK, p["mask"]),
        (PARENT_INIT, p["init"]),
        (PARENT_DIRTOK, dirtok),
        (PARENT_OUTTOK, outtok),
    ]
    child = derive_spec.derive(
        PARENT, nid,
        fresh={
            "owner": "canon-motion plate-fix lane, 2026-08-21",
            "consumer": consumer_for(row),
            "success": success_for(row),
            "why": why_for(row),
        },
        overrides={
            "seed": SEED,
            "argv:--init-sha256": init_sha,
            "argv:--note": note_for(row),
            "payload:prompt.txt": prompt,
            "payload:negative.txt": row["negative"],
            "payload:fetch_init.py": FETCH.format(
                beat=beat, init=p["init"], mask=p["mask"],
                init_sha=init_sha, mask_sha=mask_sha),
            "key:beat": beat,
            "key:priority": 18,
            "key:script_line": row["script_line"],
        },
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE INIT. Every sampler number is the b16 rung's by copy: 40 "
                "steps, cfg 7.5, strength 0.30, pad-crop 64, blur 8, seed "
                "20260820, the whole inpaint_fruit.py payload, the env block, "
                "the needs, the dry-run-before-any-model gate and the no-glob "
                "publish. The prompt and negative change because they describe "
                "a different beat, and the fetch changes because it names "
                "different files. Beat 20 additionally strikes `fruit` from "
                "the negative, because the canon purple fig is in that plate "
                "and the pad-crop can reach it.\n\n"
                "ONE CARRIED VALUE WAS NOT SAFE TO CARRY, and it is recorded "
                "rather than quietly kept: the parent's negative measures 84 "
                "CLIP tokens against a ceiling of 77. The overflow is silent "
                "and drops from the tail, so as filed the b16 rung banned "
                "nothing from `chibi` onward. It is trimmed to 60 tokens here "
                "by removing only terms another term already covers -- see the "
                "comment on NEGATIVE_BASE in the deriver. This is a fix to an "
                "unrunnable inheritance, not a second variable."),
            "init_provenance": (
                "%s/%s, 832x1216, sha256 %s, with its mask %s sha256 %s. Both "
                "are committed on origin/main -- fetch_init.py pulls them by "
                "raw URL and refuses on any sha mismatch, so an edited "
                "composite stops the job rather than quietly naturalising a "
                "different picture. The composite was drawn onto beat %02d's "
                "canon w2 plate, which is the same plate the failed motion "
                "take used, so the ONLY difference between the old init and "
                "the new one is the object the script names."
                % (p["dir"], p["init"], init_sha, p["mask"], mask_sha, beat)),
            "failure_predicted_in_advance": (
                "TWO, AND THEY ARE FILED BEFORE THE PIXELS. FIRST, THE BIG-LEAF "
                "DEGENERATE: the b16 rung named it -- the pass draws two "
                "enormous leaves that fill the crop, and detail inside the "
                "region FALLS while looking busier. If that fires here it will "
                "look like an improvement in a thumbnail and a failure at 1:1, "
                "so P1 is judged at full size. SECOND, AND SPECIFIC TO THESE "
                "THREE: the mask lies over or beside the FIGURE here, where on "
                "b16 the plate was person-free by construction. A mask that "
                "clips his arm (b02), his chest (b03) or his hand (b20) hands "
                "0.30 a licence to redraw part of him. That is what the dry "
                "step exists to catch, and it is why P4 is a killing bar "
                "rather than a note."),
            "not_done_on_purpose": (
                "NO MOTION IS RENDERED BY THIS JOB and no motion spec is filed "
                "by it. The re-derived i2v rung for this beat waits on a human "
                "opening this png, because the entire premise of the fix is "
                "that a plate must CONTAIN the object before a prompt may name "
                "it -- filing the motion job in the same breath would be "
                "asserting the plate passed before anyone looked. Beat 07 is "
                "also absent: it needs a second FIGURE, which is a two-figure "
                "skeleton route and not a masked plant composite."),
        },
        by="pipeline/derive_ep2_sapnat_0821.py",
        retoken=retoken,
    )
    out = "pipeline/jobs/%s.yaml" % nid
    return child, out, init_sha, prompt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    written = []
    for row in ROWS:
        child, out, init_sha, prompt = spec_for(row, a.force)
        print("%-24s beat %-3d init %s..  prompt %d chars"
              % (new_id(row["beat"]), row["beat"], init_sha[:12], len(prompt)))
        if a.write:
            path = derive_spec.write(child, out, force=a.force)
            written.append(path)
            derive_fetch_guard.assert_fetch_urls_resolve(
                path, must_hold=(paths_for(row["beat"])["init"],
                                 paths_for(row["beat"])["mask"]))
            print("   wrote %s  (fetch urls resolve)"
                  % os.path.relpath(path, REPO))

    if not a.write:
        print("\n3/3 derived, clip77 counted, inits hashed. "
              "-- dry run. re-run with --write.")
        return 0
    print("\nwrote %d spec(s). Enqueue with box_enqueue.py; the composite "
          "inputs are already on origin/main." % len(written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
