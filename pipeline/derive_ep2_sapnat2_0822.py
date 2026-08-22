#!/usr/bin/env python3
r"""Derive the 0.30 NATURALIZE jobs for the two LEAF-SHAPE beats, 12 and 21.

    python3 pipeline/derive_ep2_sapnat2_0822.py            # dry run
    python3 pipeline/derive_ep2_sapnat2_0822.py --write

WHAT THESE TWO BEATS HAVE IN COMMON, AND WHY THEY ARE ONE DERIVER
-----------------------------------------------------------------
Beats 12 and 21 are the only two beats in episode 2 whose ONLY remaining fault
is the SHAPE OF THE PLANT. Neither has a figure in frame, neither has a motion
problem, and both have sat with no candidate for three days behind the same
sentence on /review/ep2-beats-0821: "named, costed at about ten minutes of GPU,
not fired."

  b12  the plant is TWO PERFECT ROUND DISCS on a stem.
  b21  the plant is ONE GIANT LANCE-SHAPED LEAF standing straight up -- and
       beat 21 is otherwise the best beat in the episode, the only one whose
       definition is fully met, with the hard clause measured.

Canon is `sapling-cotyledon-shape` (founder, 2026-08-17): AVERAGE leaves, the
shape anyone draws when you say leaf, and lance shapes are ruled out by name.
It supersedes the round/oval inference drawn from the two-leaf ruling, which is
exactly what b12 is still rendering.

THE INIT IS THE CLIP'S OWN FIRST FRAME, NOT THE PLATE IT WAS HANDED
-----------------------------------------------------------------
This is the one thing in these two jobs that is not copied from the b16 rung,
and it is deliberate. Neither beat renders its init: b12's tightB take abandons
the 12-related-r4-s2 macro plate by f006 and draws the disc seedling itself, and
beat 21's own verdict in ep2-b21-daylight-0814 reads "from f007 the init is
entirely gone". Correcting the plate they were handed would correct a picture
neither clip contains. So the composite was drawn onto f000 of the SHIPPED TAKE
-- which makes the new init the take's own picture with one thing changed, and
keeps every other thing the founder has already accepted about these two beats.

WHAT IS NOT NEW HERE: NOT ONE SAMPLER NUMBER
-----------------------------------------------------------------
Everything comes from `pipeline/derive_ep2_sapnat_0821.py`, which carried it
from the b16 rung: 40 steps, cfg 7.5, strength 0.30, pad-crop 64, blur 8, the
whole inpaint_fruit.py payload, the env block, the needs, the dry-run mask gate
before any model loads, and the no-glob publish. 0.30 runs 12 of 40 steps from a
latent that still holds the drawn structure, so the layout steps never run and
the pass FINISHES a shape instead of inventing one. Six naturalize passes of
this exact recipe are on disk (beats 03, 13, 15, 16, 19 and the 08-21 tranche)
and every one of them left the plant where the compositor put it.

WHAT IS DIFFERENT, AND EACH IS FORCED BY THE MATERIAL
-----------------------------------------------------------------
  * NO FIGURE. The 0821 rows all read "with one small green goblin <doing X>
    behind it" because they naturalise a plant into a character plate. These
    two frames have no person in them at all, so the clause is struck and
    `1boy, 2boys, goblin, man, person` go into the NEGATIVE instead. P4 of the
    0821 bar -- "he survives unchanged" -- has nothing to be true of here and
    is replaced by P4' below, which is about the BACKDROP surviving.
  * 704x1280, not 832x1216. The inpaint driver takes its size from the init, so
    this needs no argument; it is stated because every previous naturalize in
    this tree was 832x1216 and a reader will assume it.

THE TWO FAULTS I AM CARRYING IN ON PURPOSE, both named in the bar rather than
hidden: b12's composite keeps a ~30x50 px black twig fragment at the grass line
(the class map protects the grass band from the erase, and the twig sits inside
it), and b21's keeps a thin sliver of the old pale stem beside the new one. Both
lie INSIDE the inpaint mask, so this pass is the thing that gets to fix them --
which is why they are a bar clause and not a re-composite.

$0 to derive. ~4 GPU minutes each.
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
import derive_ep2_sapnat_0821 as P                            # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77     # noqa: E402

PARENT = P.PARENT
PARENT_ID = P.PARENT_ID
PARENT_PUBDIR = P.PARENT_PUBDIR
PARENT_DIRTOK = P.PARENT_DIRTOK
PARENT_INIT = P.PARENT_INIT
PARENT_MASK = P.PARENT_MASK
PARENT_OUTTOK = P.PARENT_OUTTOK
SEED = P.SEED

# The 0821 fetch template with its year-day token moved. Every 0821 in it is a
# PATH: the box work dir, the raw URL directory and the User-Agent. Nothing
# semantic changes, which is why this is a substitution rather than a copy.
FETCH = P.FETCH.replace("0821", "0822").replace(
    # ...and the box WORK DIR gets the "2" the steps already carry. The retoken
    # renames the parent's dirtok b16sapcomp-r2-0820 -> bNNsapnat2-0822 in every
    # step argv, but the fetch script is a payload STRING that the retoken does
    # not reach, so the first filing wrote the init to bNNsapnat-0822 and the dry
    # step read bNNsapnat2-0822 and died with "init not found" -- rc=2 on both
    # jobs, five seconds each, caught before a model loaded. The URL directory
    # (ep2-bNN-sapnat-0822) is a REPO path and must NOT get the "2"; only the
    # box-side OUT does, which is why this substitution has no leading hyphen.
    "b{beat:02d}sapnat-0822", "b{beat:02d}sapnat2-0822")

PLANT = P.PLANT

# NO FIGURE IN EITHER PLATE, so the figure bans are the ones that matter: this
# pass has a licence to redraw the masked region and the one thing it must not
# do is put a person in it. `plant girl, alraune` were already in the 0821 base
# for the same reason one level down.
NEGATIVE = (P.NEGATIVE_BASE
            .replace("second plant, plant girl, alraune, child",
                     "second plant, plant girl, alraune, child, 1boy, 2boys, "
                     "goblin, man, person"))

BAR = """JUDGED BY EYE AT 1:1, AND THE QUESTION IS THE LEAF SHAPE.

  P1  THE PLANT IS DRAWN, NOT PASTED. The two blades and the stem carry cel
      shading and the plate's own ink line weight. The compositor's flat fill
      and its hard cut edge are gone.
  P2  IT HAS NOT MOVED. Stem root, height and leaf tips sit where the
      compositor put them, within a few px. 0.30 finishes a structure; if the
      plant has relocated, the strength was wrong and the number is the fix.
  P3  EXACTLY TWO AVERAGE LEAVES ON ONE STEM. Canon sapling-two-leaves plus
      sapling-cotyledon-shape. THIS IS THE WHOLE POINT OF BOTH JOBS: a round
      disc is what beat 12 already has and a lance is what beat 21 already
      has, so either shape coming back is a FAIL even though it would look
      like a competent picture. Three leaves, leaflets, a branching stem or a
      second plant is also a FAIL.
  P4' THE BACKDROP SURVIVES. Beat 12's cumulus bank and beat 21's hedgerow,
      golden field and cloud bands are the parts of these two frames the
      founder has already accepted. The mask is local; anything outside it
      that has changed means the pad-crop reached further than the geometry
      said and the plate is a FAIL.
  P5  IT SITS IN THE GRASS. Contact where the stem meets the ground, no
      floating base, no halo of untouched pixels at the mask edge.

  P6  THE TWO CARRIED-IN BLEMISHES ARE GONE OR HARMLESS, and they are named in
      advance so a lane cannot discover them afterwards and call them new.
      b12: a ~30x50 px black twig fragment at the grass line beside the stem,
      left standing because the class map protects the grass band from the
      erase. b21: a thin sliver of the OLD pale stem beside the new one below
      the hedgerow line. Both are inside the mask. If either survives as a
      readable SECOND STALK the plate fails P3 on the count; if it comes back
      as one more blade of grass, that is a pass and it is said out loud.

  ALSO EXPECTED AND NOT A FAULT: b12's erase left a horizontal smear across
  the cloud bank where two 250 px discs were filled from their boundary. It is
  inside the mask, and repainting it is a thing this pass may legitimately be
  asked to do -- 20% of the frame is masked here against b16's 5%. If the
  smear survives, THAT is the finding: 0.30 finishes a drawn structure and a
  boundary-fill smear is a structure, so the fix would be a wider erase and a
  redrawn sky rather than a higher strength.

A FAIL on P2 or P4' kills the plate. A FAIL on P1 alone is a strength question
and is worth one more round; a FAIL on P3 is a compositor question and goes
back to the drawing, not to the sampler."""


def new_id(beat: int) -> str:
    return "ep2-b%02d-sapnat2-0822" % beat


def sha256_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def paths_for(beat: int) -> dict:
    d = "farm-out/ep2-b%02d-sapnat-0822" % beat
    init = "b%02d-sapnat-in-0822.png" % beat
    mask = "b%02d-sapnat-in-mask-0822.png" % beat
    return {"dir": d, "init": init, "mask": mask,
            "init_abs": os.path.join(REPO, d, init),
            "mask_abs": os.path.join(REPO, d, mask)}


ROWS = [
    {
        "beat": 12,
        "scene": ("close on the whole seedling against a bright bank of "
                  "cumulus cloud"),
        "object": "two average cotyledon leaves in place of two round discs",
        "was": ("TWO PERFECT ROUND DISCS on a stem -- the round/oval inference "
                "that the 08-17 cotyledon ruling superseded by name"),
        "script_line": ("Beat 12 RELATED: the sapling stands perfectly still "
                        "against the sky. The approved line says 'perfectly "
                        "still', so nothing about the STAGING moves here -- "
                        "only the shape of the two leaves."),
        "shipping_fault": ("the sapling GROWS across the shot, apex up 140 px "
                           "/ 11% of frame height, against an approved line "
                           "that says 'perfectly still'"),
    },
    {
        "beat": 21,
        "scene": ("standing in a golden meadow at sunset with a dark hedgerow "
                  "behind"),
        "object": "two average cotyledon leaves in place of one giant lance leaf",
        "was": ("ONE GIANT LANCE-SHAPED LEAF standing straight up, failing "
                "sapling-two-leaves and sapling-cotyledon-shape at once"),
        "script_line": ("Beat 21 THE ANSWER: the leaf tilts, steadily, in one "
                        "direction, and stops. The MOTION of this beat is the "
                        "one thing in episode 2 that is fully measured and "
                        "passing; this job does not touch it."),
        "shipping_fault": ("nothing -- beat 21 is the only beat whose "
                           "definition is fully met on all four clauses, and "
                           "the plant is its single open R4 question"),
    },
]


def prompt_for(row: dict) -> str:
    return ("%s, %s, detailed cinematic anime, masterpiece, best quality, "
            "very aesthetic" % (PLANT, row["scene"]))


def why_for(row: dict) -> str:
    return (
        "BEAT %02d'S ONLY REMAINING FAULT IS THE SHAPE OF ITS PLANT, AND A "
        "SHAPE IS A DRAWING PROBLEM.\n\n"
        "What is in the cut today: %s. Canon since the founder's 2026-08-17 "
        "ruling is AVERAGE leaves -- 'the shape anyone draws when you say "
        "leaf' -- and it supersedes the earlier inference by name.\n\n"
        "THE WORDING LADDER FOR THIS IS CLOSED AND WAS CLOSED BY MEASUREMENT. "
        "Cardinality and leaf shape are Class A in "
        "pipeline/composite-init-pattern.md: the strongest wording available "
        "-- the numeral plus explicit negation of every wrong count -- "
        "returned 0 of 16 frames with two correct leaves. The instrument that "
        "works is the composite, and it is now four for four on plants (beats "
        "03, 13, 16, 19) with a fifth finding from last night that matters "
        "here: beat 19 proved a hand-drawn COMPOSITED object survives i2v "
        "motion. That was the missing evidence under this whole route, and "
        "beats 12 and 21 are two of the four beats it unblocks.\n\n"
        "WHAT THIS JOB IS AND IS NOT. It naturalises the drawn plant into the "
        "frame's dialect at strength 0.30 and stops. It renders no motion, it "
        "files no motion spec, and it does not touch review/ep2-ship-0821 -- "
        "the take in the cut is unaffected until a human opens this png. "
        "Beat %02d's shipping status is unchanged: %s."
        % (row["beat"], row["was"], row["beat"], row["shipping_fault"]))


def consumer_for(row: dict) -> str:
    return (
        "THE INIT FOR BEAT %02d'S RE-RENDERED MOTION, and nothing else until "
        "a human has opened it. Named consumer: this same lane's motion rung, "
        "which cannot be filed before the plate exists -- the founder's page "
        "has carried 'named, not fired' on this beat for three days and the "
        "thing that was not fired is precisely this pass. No cut changes "
        "because this landed; /review/ep2-beats-0821 gains a CANDIDATE only "
        "after the motion render off this plate is judged."
        % row["beat"])


def success_for(row: dict) -> str:
    return (
        "ONE 704x1280 png in which %s IS DRAWN INTO THE FRAME AND HAS NOT "
        "MOVED, judged by eye at 1:1 and not by a metric. P1 cel shading and "
        "the plate's ink weight, not the compositor's flat fill; P2 root, "
        "height and leaf tips within a few px of where they were composited; "
        "P3 exactly two AVERAGE leaves on one stem -- a disc or a lance "
        "coming back is a FAIL however well drawn; P4' the backdrop outside "
        "the mask is untouched; P5 the stem makes contact with the ground. "
        "The named degenerate outcome is a RELOCATED or REGROWN plant: if "
        "0.30 has moved it or given it a third leaf, this plate is a FAIL and "
        "the fix is the number or the drawing, not another seed."
        % row["object"])


def note_for(row: dict) -> str:
    return (
        "ATTACHED TO BOTH THE DRY STEP AND THE RENDER STEP, and true of each. "
        "ON THE DRY STEP it is a MASK GEOMETRY CHECK: it writes the mask and "
        "exits BEFORE a model is loaded, so a wrong mask costs seconds instead "
        "of a GPU fire. WHAT TO CHECK on beat %02d: (1) one connected blob "
        "shaped like a stem with two leaves plus the region the OLD plant was "
        "erased out of -- this mask is deliberately larger than the b16 rung's "
        "because it has to cover the hole as well as the drawing; (2) it does "
        "not reach the top of the frame; (3) THERE IS NO PERSON IN THIS PLATE "
        "and the negative bans one, so a figure appearing inside the mask is a "
        "hard fail and not a curiosity. ON THE RENDER STEP: one pass, one "
        "seed. 0.30 runs 12 of 40 steps from a latent that still holds the "
        "drawn structure, so the layout steps never run and the pass FINISHES "
        "the shape rather than inventing one." % row["beat"])


def spec_for(row: dict, force: bool):
    beat = row["beat"]
    nid = new_id(beat)
    p = paths_for(beat)
    for f in (p["init_abs"], p["mask_abs"]):
        if not os.path.isfile(f):
            raise SystemExit("!! missing composite input %s" % f)
    init_sha, mask_sha = sha256_of(p["init_abs"]), sha256_of(p["mask_abs"])
    prompt = prompt_for(row)
    assert_under_clip77("b%02d prompt" % beat, prompt)
    assert_under_clip77("b%02d negative" % beat, NEGATIVE)

    dirtok = "b%02dsapnat2-0822" % beat
    outtok = "b%02d-sapnat2" % beat
    retoken = [
        (PARENT_ID, nid),
        ("ep2-" + PARENT_PUBDIR.split("ep2-")[1], "ep2-b%02d-sapnat2-0822" % beat),
        (PARENT_MASK, p["mask"]),
        (PARENT_INIT, p["init"]),
        (PARENT_DIRTOK, dirtok),
        (PARENT_OUTTOK, outtok),
    ]
    child = derive_spec.derive(
        PARENT, nid,
        fresh={
            "owner": "morning compositor lane, 2026-08-22",
            "consumer": consumer_for(row),
            "success": success_for(row),
            "why": why_for(row),
        },
        overrides={
            "seed": SEED,
            "argv:--init-sha256": init_sha,
            "argv:--note": note_for(row),
            "payload:prompt.txt": prompt,
            "payload:negative.txt": NEGATIVE,
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
                "THE INIT, and within the init the LEAF SHAPE. Every sampler "
                "number is the b16 rung's by copy through "
                "derive_ep2_sapnat_0821: 40 steps, cfg 7.5, strength 0.30, "
                "pad-crop 64, blur 8, seed 20260820, the whole "
                "inpaint_fruit.py payload, the env block, the needs, the "
                "dry-run-before-any-model gate and the no-glob publish. The "
                "prompt changes because it describes a different scene and "
                "the FIGURE CLAUSE IS STRUCK -- there is no person in either "
                "of these two plates, which is the one structural difference "
                "from every naturalize before it, and the figure words move "
                "to the negative so the pass cannot invent one."),
            "init_provenance": (
                "%s/%s, 704x1280, sha256 %s, with its mask %s sha256 %s. Both "
                "are committed on origin/main -- fetch_init.py pulls them by "
                "raw URL and refuses on any sha mismatch. THE SOURCE FRAME IS "
                "f000 OF THE SHIPPED TAKE, not this beat's render plate, and "
                "that is deliberate: neither beat renders its init (b12's "
                "take abandons the r4-s2 macro by f006, and beat 21's own "
                "verdict records 'from f007 the init is entirely gone'), so "
                "the picture to correct is the one the model settled on. The "
                "composite was cut by pipeline/beat16_sapling_composite.py, "
                "which erased the old plant out of the pixels first and drew "
                "the canon two-leaf sapling in its place; its geometry json "
                "is beside the png."
                % (p["dir"], p["init"], init_sha, p["mask"], mask_sha)),
            "failure_predicted_in_advance": (
                "THREE, FILED BEFORE THE PIXELS. FIRST, THE BIG-LEAF "
                "DEGENERATE the b16 rung named: the pass draws two enormous "
                "leaves that fill the crop and detail inside the region FALLS "
                "while looking busier. It looks like an improvement in a "
                "thumbnail and a failure at 1:1, so P1 and P3 are judged at "
                "full size. SECOND, AND SPECIFIC TO BEAT 12: its mask is 20% "
                "of the frame against b16's 5%, because it has to cover the "
                "hole where two 250 px discs were erased as well as the new "
                "plant -- and /review/ep2-b16-leaf-0820 measured 0.30 doing "
                "NOTHING on a mask eight times the working size. If b12 comes "
                "back unchanged inside the region while b21 (16%) comes back "
                "drawn, the mask-area law has a second data point and the fix "
                "for b12 is a smaller erase, not a higher strength. THIRD: a "
                "PERSON in the frame. Both plates are empty of people and the "
                "0821 prompts all named a goblin; striking that clause is the "
                "edit most likely to have an effect nobody predicted."),
            "not_done_on_purpose": (
                "NO MOTION IS RENDERED BY THIS JOB and no motion spec is "
                "filed by it, even though both beats' motion is the actual "
                "deliverable and the card is free. The premise of the whole "
                "route is that a plate must CONTAIN the object before a "
                "prompt may name it; filing the motion in the same breath "
                "would assert this plate passed before anyone looked at it. "
                "Beats 16 and 19 are also absent from this deriver and they "
                "are the other two beats on the same queue: b16's foreground "
                "grass is a blown-out bokeh whose green p88 is (239,255,230), "
                "so the tool draws a WHITE plant on it and the placement "
                "question is open; b19 needs a fig rather than a sapling and "
                "goes through the b19 drop compositor."),
        },
        by="pipeline/derive_ep2_sapnat2_0822.py",
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
        print("%-26s beat %-3d init %s..  prompt %d chars"
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
        print("\n2/2 derived, clip77 counted, inits hashed. "
              "-- dry run. re-run with --write.")
        return 0
    print("\nwrote %d spec(s). Enqueue with box_enqueue.py; the composite "
          "inputs are already on origin/main." % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
