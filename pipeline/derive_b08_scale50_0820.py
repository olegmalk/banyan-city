#!/usr/bin/env python3
r"""Derive `ep2-b08-scale50-0820` FROM `ep2-b08-grip-0820`.

THE ONE VARIABLE: `--scale2`, 0.3 -> 0.5. Nothing else moves -- and in
particular THE PROMPT DOES NOT MOVE. Same two nets, same two hints (both
byte-identical), same capsule masks, same references, same ip-scale, same first-
net scale, same seed, and the SAME 73-token prompt the parent rendered from,
including its grip clause.

WHY, IN ONE PARAGRAPH. The parent asked whether words could put a hand on the
board and got a compound answer: the grip clause DID summon articulated fingers
and a thumb onto the correct far hand, and the clipboard DISAPPEARED -- the
authored quad went from 75.8% dark pixels to 23.5% with every conditioning input
identical. The guard also went bald against canon at unchanged conditioning. So
two things are now known and one is not. Known: wording can summon a grip;
wording at this token count crowds the frame. NOT known: WHETHER THE BOARD AND
THE GRIP COMPETE FOR ONE CONDITIONING BUDGET. They have never been asked for
together at a strength that could carry both -- the board was measured at 0.3
against a 64-token prompt with no grip language, and the grip language has only
ever been tried at 0.3.

WHY 0.5 AND WHY THE SCALE RATHER THAN THE WORDS. The route's own history brackets
the answer: at 1.0+0.8 the frame flattened and the drawing died; at 1.0+0.3 the
drawing is intact and the board is marginal enough that nine words removed it.
0.5 sits between the value that is demonstrably too weak to hold an object
against a crowded prompt and the value that is demonstrably too strong to leave
the drawing alone, and closer to the former. It is a reasoned starting point, not
a measured optimum, and it is labelled as one. The alternative lever -- taking
the nine words back out -- answers nothing: that frame already exists and is
ep2-b08-scale30-0820.

WHAT THE THREE OUTCOMES MEAN, and all three are worth the 30 seconds.
  * Board back AND fingers kept -> beat 08 has its recipe, and 0.8's damage was
    the far end of a usable range rather than a verdict on composing two nets.
  * Board back, hair still bald -> the two failures are INDEPENDENT: the object
    is a conditioning-strength problem and the hair is a token-budget problem,
    and the wording has to come back out on its own rung.
  * Neither back -> the second net cannot hold an object against a crowded
    prompt at any strength that leaves the drawing alone, and figure ink in the
    board hint becomes the ARGUED next lever instead of the speculative one.

$0. Writes one yaml file. No GPU, no network, nothing enqueued.
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import clip_token_count  # noqa: E402
import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b08-grip-0820.yaml"
PARENT_ID = "ep2-b08-grip-0820"
NEW_ID = "ep2-b08-scale50-0820"
OUT = "pipeline/jobs/%s.yaml" % NEW_ID

STAGE = r"C:\banyan-farm\b08scale50-0820\src"
REPO_COMMIT = "ee74ac0e3eaf920fc7637fa7e4f2727af7684628"

TWINS_DIR = r"C:\banyan-farm\cnet-openpose-twins"
SCRIBBLE = "xinsir/controlnet-scribble-sdxl-1.0"
DRIVER = "pipeline/controlnet_plate.py"
DRIVER_SHA = "aff188907fa03914b30a8cec2e5f739a5c4941f5d4246f4b2e220a9cc047c66a"
POSE_HINT = "pipeline/control/b08-openpose-nat-0819.png"
POSE_SHA = "562911c8174a6ecc21bc8710a1ac1b7f965c3f2d865093a742c2598c37d952e0"
BOARD_HINT = "pipeline/control/b08-board-0820.png"
BOARD_SHA = "38cd39da304dbb0317aa2522e1ccca099bef583e88e6573fde03b287358213d6"
REF_GOBLIN = "pipeline/control/b08-ref-goblin-0819.png"
REF_GOBLIN_SHA = "13b0c69d2f95dad6fd5472d8ab0310967b1a88c4554de7e6ff74b2d3e3644d8c"
REF_GUARD = "pipeline/control/b08-ref-guard-0819.png"
REF_GUARD_SHA = "61dc3f7fbd052617e52db63e8f6d359822b6ceba14b13514ffc03179b56cd83c"

SEED = 20260819
OLD_SCALE2 = "0.3"
NEW_SCALE2 = "0.5"
GRIP_CLAUSE = "fingers and thumb gripping the clipboard edge"


def main() -> int:
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    import yaml as _yaml
    parent = _yaml.safe_load(open(os.path.join(root, PARENT), encoding="utf-8"))
    ppay = {os.path.basename(k.replace("\\", "/")): v
            for k, v in parent["payload"].items()}
    clip = clip_token_count.Clip()
    n_p, _ = clip.count(ppay["prompt.txt"])
    total = n_p + clip_token_count.SPECIALS
    assert total == 73, "the parent prompt no longer measures 73: %d" % total

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "beat 08 staging lane, 2026-08-20 -- derived by "
                     "pipeline/derive_b08_scale50_0820.py, on the rung its own "
                     "parent's verdict named. Fired immediately because the "
                     "card was idle with nothing claimed and nothing waiting.",
            "consumer":
                "Beat 08's plate, and the question is now sharper than it has "
                "been on this route. The parent proved words can summon a grip "
                "and proved that summoning it at 0.3 costs the clipboard "
                "entirely. What the cut needs to know is whether those two "
                "clauses are COMPETING FOR ONE CONDITIONING BUDGET or failing "
                "for unrelated reasons, because the first is fixable with a "
                "number and the second is not.",
            "success":
                "One 832x1216 png with its sidecar, published to "
                "C:\\banyan-farm\\courier-box\\farm-out\\ep2-b08-scale50-0820 "
                "with a sha256 manifest, and read at 1:1, 3x and 5x beside BOTH "
                "predecessors -- ep2-b08-scale30-0820, which has the board and "
                "a mitten, and ep2-b08-grip-0820, which has the fingers and no "
                "board. This rung is asking for one frame with both. The "
                "preflight must print its four verification lines and the "
                "sidecar must read `controlnet_2_conditioning_scale: 0.5` with "
                "the prompt still carrying `%s`." % GRIP_CLAUSE,
            "why":
                "One number, one sample, thirty seconds of GPU, and all three "
                "outcomes are informative -- including the one that closes the "
                "route to further tuning and sends it to the hint. Every weight "
                "is on the card, both hints are byte-identical to three frames "
                "already rendered, and the previous two rungs took 22 seconds "
                "of render each.",
        },
        overrides={
            "argv:--arm": "scale50",
            "argv:--scale2": NEW_SCALE2,
            "argv:--repo-commit": REPO_COMMIT,
            "seed": SEED,
        },
        retoken=[("b08grip-0820", "b08scale50-0820"),
                 ("ep2-b08-grip-0820-grip", "ep2-b08-scale50-0820-scale50")],
        by="pipeline/derive_b08_scale50_0820.py",
        extra={
            "bar": {
                "b0_the_stack_is_what_it_claims":
                    "VOID-CHECK, unchanged from the parent except the one "
                    "number. Preflight prints `twins net verified`, `scribble "
                    "net verified`, the line asserting the two nets share size "
                    "and config and DIFFER in weights, and `staged driver, BOTH "
                    "hints and BOTH references verified`. The sidecar must read "
                    "`controlnet_2_conditioning_scale: 0.5` -- if it reads 0.3 "
                    "the override did not take and the frame is a re-run of the "
                    "parent -- with `controlnet_conditioning_scale: 1.0`, `seed: "
                    "20260819`, both hint shas and both capsule masks unchanged, "
                    "and the prompt still carrying the grip clause.",
                "b4a_the_board_AND_the_grip":
                    "THE WHOLE POINT, AND IT IS SCORED AS ONE CLAUSE BECAUSE "
                    "THE QUESTION IS WHETHER THEY COEXIST. (i) A flat board or "
                    "clipboard legibly drawn at the authored quad -- corners "
                    "(608.6,660.5) (719.5,678.1) (697.7,816.2) (586.7,798.6), "
                    "bbox x 583-723 y 657-820, top edge below the shoulder line "
                    "y=491. Measured the way the parent's loss was measured: "
                    "FRACTION OF PIXELS IN THAT BBOX BELOW LUMA 80, against "
                    "0.758 when the board was present and 0.235 when it was "
                    "gone. (ii) Separated digits at the board's edge at 5x, on "
                    "the far hand, with the board passing behind or between them "
                    "rather than tucking under a rounded form. PASS needs BOTH. "
                    "Board with a mitten repeats scale30 and is scored as such; "
                    "fingers with no board repeats the parent.",
                "b8_the_guard_has_hair":
                    "canon.yaml `ep2-guard-hair` -- guard B has light sandy "
                    "hair, \\bbald\\b FORBIDDEN, and beat 08 is now IN that "
                    "entry's scope as of 2026-08-20. THE INSTRUMENT NOW HAS TWO "
                    "INPUTS AND THIS RUNG MOVES ONE OF THEM. It reads bald under "
                    "conditioning load (1.0+0.8) and read bald again under "
                    "prompt crowding (73 tokens at 1.0+0.3). This frame raises "
                    "the conditioning while holding the crowding, so a bald "
                    "guard here is EXPECTED if the two effects add and is the "
                    "cheapest evidence that they do. Sandy hair at 1.0+0.5 with "
                    "73 tokens would mean they do not simply add, and that is "
                    "worth as much as the board.",
                "b6_drawn_not_traced":
                    "THE CLAUSE 0.8 BROKE, AND 0.5 IS THE FIRST VALUE ABOVE 0.3 "
                    "ANYONE HAS TRIED. Both figures read as DRAWN CHARACTERS at "
                    "ep2-b08-twinsipa-0819's standard: pupils and a set jaw, "
                    "hair with strands where there is hair, folds in BOTH "
                    "garments, a legible metal clasp, a drawn cuff, separated "
                    "digits. At 0.8 this collapsed into one flat robe. If it "
                    "degrades at 0.5 the usable range is narrower than 0.3-0.8 "
                    "and the route needs to know before it tunes anything else.",
                "b4b_both_arms_stay_on_their_skeletons":
                    "B4b-i: the pointing hand's centroid within ~60 px of the "
                    "authored wrist (280.5,695.1) -- twinsipa 40.3, boardnet "
                    "10.2, scale30 48.5, grip 41.2, never failed. B4b-ii: THE "
                    "GUARD MUST HAVE TWO ARMS, both ending in drawn hands. "
                    "boardnet lost the far arm into the robe at 0.8 and that is "
                    "the specific 0.8 damage this value is testing the near edge "
                    "of.",
                "b7_no_limb_fragmentation":
                    "G-R at six regions, three per figure, EVERY BOX PLACED "
                    "FRESH ON THIS FRAME and publishing coordinates, luma AND "
                    "material. Within-figure spread <= 25.0; every guard region "
                    "<= 0.0, every goblin region >= +20.0. TWO STANDING "
                    "ADMISSIBILITY RULES, both earned on this beat: boxes do not "
                    "transfer between frames because wardrobe moves under them "
                    "(scale30), and ON THE GUARD A COLOUR PREDICATE CANNOT "
                    "DECIDE THE MATERIAL -- his cream shirt reads R-B 34.7 "
                    "against his skin's 42.6-49.7, and a colour-picked box "
                    "landed on a sleeve at 100% 'pale' (grip). Guard boxes are "
                    "placed by eye at 5x and published with their R-B.",
                "b2_the_identities_separate":
                    "Guard face <= 0.0, goblin face >= +20.0, separation >= "
                    "+20.0. twinsipa +42.0, scale30 +60.6, grip +54.4. Same "
                    "material-and-luma publication rule as B7.",
                "b4c_the_arm_belongs_to_the_guard":
                    "MUST SURVIVE. The pointing arm grows from the guard's "
                    "shoulder and is human-skinned. Ten mechanisms have held it.",
                "b1_the_pair":
                    "TWO figures and only two, both whole, under "
                    "figure_count_ruled_from_the_script_0817. AND EXACTLY ONE "
                    "BOARD if a board arrives: the prompt names `clipboard` "
                    "twice and a stronger object net is the condition under "
                    "which that repetition could finally duplicate it.",
                "b3_one_ground_plane":
                    "Both stand on the same grass. Read by eye if the automated "
                    "detector is confounded by foreground grass.",
                "b5_no_colossus":
                    "Neither figure towers; twinsipa measured a stature ratio "
                    "near 1.13 against the authored 1.100. BULK is scored under "
                    "B6.",
            },
            "the_number_is_reasoned_not_measured":
                "SAID PLAINLY SO NOBODY LATER CITES 0.5 AS AN OPTIMUM. 1.0+0.8 "
                "flattened the frame and killed the drawing. 1.0+0.3 leaves the "
                "drawing alone and is too weak to hold the object against a "
                "73-token prompt. 0.5 is between them and nearer the value that "
                "works. That is an argument, not a measurement, and this sample "
                "is the measurement.",
            "not_done_on_purpose":
                "ONE sample, ONE arm, ONE number. THE PROMPT IS NOT TOUCHED -- "
                "not one token, in either direction. Taking the nine words back "
                "out answers nothing, because that frame already exists and is "
                "ep2-b08-scale30-0820; leaving them in is what makes this a test "
                "of whether the board and the grip compete. No sweep: if 0.5 is "
                "wrong the next sample moves it once more. No per-net guidance "
                "window -- rung 17 excluded it. No figure ink in the board hint, "
                "which is what this rung's failure would finally license as an "
                "argued lever. No change to either hint, the masks, the "
                "references, the ip-scale, the first net's scale or the seed. No "
                "second seed. No third figure. No colour-cast fix. No pick, no "
                "plate_ack, no canon filename, no canon.yaml edit.",
            "rights_and_weights":
                "THIS IS THE `licence_note`. Unchanged and clean. Base "
                "cagliostrolab/animagine-xl-3.1 (CreativeML Open RAIL++-M). Net "
                "1 xinsir/controlnet-openpose-sdxl-1.0 twins variant, "
                "apache-2.0. Net 2 xinsir/controlnet-scribble-sdxl-1.0, "
                "apache-2.0, no attribution condition. IP-Adapter "
                "h94/IP-Adapter, apache-2.0. Both references are repo-internal "
                "crops. BOTH hints are authored in PIL from numbers -- no "
                "annotator, so the lllyasviel/Annotators landmine is untouched "
                "by either condition. MistoLine is not used.",
            "scoring_rule_pre_registered":
                "THIS IS THE `verdict_rule`, WRITTEN BEFORE THE PIXELS.\n"
                "(1) BOARD BACK AND THE FINGERS KEPT, DRAWING INTACT -> the two "
                "clauses were competing for one budget, beat 08 has a COMPLETE "
                "plate candidate, and 0.8's damage was the far end of a usable "
                "range rather than a verdict on composing two nets. Still NOT a "
                "pick and NOT a plate_ack; that is R4's.\n"
                "(2) BOARD BACK, FINGERS GONE -> they compete and the budget "
                "cannot hold both. The object wins on this route and the grip "
                "goes to the hint, which is then an argued lever with evidence "
                "rather than a guess.\n"
                "(3) BOARD BACK, HAIR STILL BALD -> the object failure and the "
                "canon failure are INDEPENDENT: one is conditioning strength, "
                "one is token budget. Not a pass, and it splits the remaining "
                "work cleanly in two.\n"
                "(4) NEITHER BACK -> the second net cannot hold an object "
                "against a crowded prompt at any strength that leaves the "
                "drawing alone. The route stops tuning numbers; figure ink in "
                "the board hint becomes the named lever and it now has the "
                "argument the five tracing losses are owed.\n"
                "(5) THE DRAWING DEGRADES AT 0.5 -> the usable range is "
                "narrower than 0.3-0.8, which is a finding about the pair of "
                "nets that outlives beat 08 and constrains any other beat that "
                "wants a second condition.",
            "who_ruled_this_rung":
                "ep2-b08-grip-0820's own verdict, under "
                "`next_rung_named_not_taken`: \"ONE sample, and the variable is "
                "--scale2, WITH THIS FRAME'S WORDING HELD... Holding the "
                "73-token prompt byte-identical and raising --scale2 from 0.3 "
                "toward ~0.5 asks exactly that in one number.\" Route log "
                "pipeline/b08-arm-route-0819.md section 18 says the same. Fired "
                "immediately rather than left for a human hour: the card was "
                "measured IDLE with nothing claimed and nothing waiting, and "
                "this job has no dependency -- every weight is local and both "
                "hints already exist. Written in an `extra` key because `fresh` "
                "prose is retokened and a parent id there would become this "
                "job's own id.",
            "why_these_key_names":
                "`scoring_rule_pre_registered` and `rights_and_weights` are this "
                "spec's `verdict_rule` and `licence_note`. derive_spec's "
                "FINDINGS_NAME guard refuses any extra key matching "
                "/verdict|licen[cs]/, which is right for findings and "
                "over-reaches on two house keys that must be written BEFORE the "
                "pixels. Same declaration the last four rungs made.",
        },
    )

    step = [s for s in child["steps"] if s["name"] == "grip"][0]
    step["name"] = "scale50"

    argvs = [str(a) for s in child["steps"] for a in s["argv"]]

    def flag(n):
        return [argvs[i + 1] for i, v in enumerate(argvs) if v == n]

    assert flag("--scale2") == [NEW_SCALE2], flag("--scale2")
    assert OLD_SCALE2 not in flag("--scale2"), "the old scale survived"
    assert flag("--scale") == ["1.0"], flag("--scale")
    assert flag("--seed") == [str(SEED)], flag("--seed")
    assert flag("--controlnet") == [TWINS_DIR]
    assert flag("--controlnet2") == [SCRIBBLE]
    assert flag("--control") == [POSE_HINT]
    assert flag("--control-sha256") == [POSE_SHA]
    assert flag("--control2") == [BOARD_HINT]
    assert flag("--control2-sha256") == [BOARD_SHA]
    assert flag("--ip-ref") == [REF_GOBLIN, REF_GUARD]
    assert flag("--ip-ref-sha256") == [REF_GOBLIN_SHA, REF_GUARD_SHA]
    assert flag("--ip-scale") == ["0.7"]
    assert len(flag("--ip-mask-capsules")) == 2
    assert flag("--arm") == ["scale50"], flag("--arm")
    assert flag("--root") == [STAGE], flag("--root")
    assert flag("--repo-commit") == [REPO_COMMIT], flag("--repo-commit")
    assert [s["name"] for s in child["steps"]] == ["preflight", "scale50",
                                                   "publish"]

    pargv = [str(a) for s in parent["steps"] for a in s["argv"]]
    assert flag("--ip-mask-capsules") == [pargv[i + 1] for i, v in
                                          enumerate(pargv)
                                          if v == "--ip-mask-capsules"], \
        "the capsule masks moved"

    runnable = "\n".join(argvs + list(child.get("payload") or {})
                         + [str(x) for x in (child.get("artifacts") or [])])
    assert PARENT_ID not in runnable, "the parent id survived a runnable path"

    # ---- THE WORDS DID NOT MOVE. This is the assertion the whole rung rests on.
    cpay = {os.path.basename(k.replace("\\", "/")): v
            for k, v in child["payload"].items()}
    assert cpay == ppay, "the prompt or the negative drifted from the parent's"
    assert GRIP_CLAUSE in cpay["prompt.txt"], "the grip clause must stay in"
    assert "light sandy hair" in cpay["prompt.txt"]
    assert "bald" not in cpay["prompt.txt"], "canon ep2-guard-hair forbids bald"

    for rel, want in ((DRIVER, DRIVER_SHA), (POSE_HINT, POSE_SHA),
                      (BOARD_HINT, BOARD_SHA), (REF_GOBLIN, REF_GOBLIN_SHA),
                      (REF_GUARD, REF_GUARD_SHA)):
        with open(os.path.join(root, rel), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        assert got == want, "%s is %s, spec pins %s" % (rel, got, want)

    out = derive_spec.write(child, OUT)
    print("wrote %s" % out)
    print("id        %s" % child["id"])
    print("parent    %s" % PARENT_ID)
    print("variable  --scale2 %s -> %s (the prompt is byte-identical)"
          % (OLD_SCALE2, NEW_SCALE2))
    print("prompt    %d of 77, unchanged, grip clause intact" % total)
    print("steps     %s" % " -> ".join(s["name"] for s in child["steps"]))
    print("stage     %s" % STAGE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
