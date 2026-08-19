#!/usr/bin/env python3
r"""Derive `ep2-b08-scale30-0820` FROM `ep2-b08-boardnet-0820`.

THE ONE VARIABLE: `--scale2`, 0.8 -> 0.3. Nothing else moves. Same two nets,
same two hints (both byte-identical), same capsule masks, same references, same
ip-scale, same first-net scale, same seed, same words.

WHY, IN ONE PARAGRAPH. The parent composed multi-ControlNet on the first try
and DELIVERED THE BOARD -- a flat quad at the authored place and tilt, the
first object beat 08 has ever produced -- and lost almost everything else
doing it: the guard's two frozen garments collapsed into one flat robe, his far
arm vanished so no hand holds the board, he came back BALD against canon, and
the frame darkened from mean luma 141.6 to 86.9 with the light turning hard and
directional. The parent's verdict identified the mechanism: A SPARSE HINT IS
NOT A WEAK HINT. The board hint is 99.7% black, and for a scribble net a black
pixel is not an absence of instruction -- it is "no edge here". So a
nearly-black hint asserts "no edges anywhere" across the whole frame, at 0.8,
for the full denoise, with its residuals ADDED to the pose net's at 1.0. The
strength is wrong, not the mechanism.

WHY 0.3 AND NOT A SWEEP. `ONE SAMPLE BEFORE ANY BATCH`, and the parent's
verdict said so in as many words: "ONE sample at one lower value, then look."
0.3 is chosen as roughly the fraction that would put the SUM of the two
conditioning scales (1.0 + 0.3 = 1.3) near the load the beat has actually
rendered well under, rather than the 1.8 that flattened this frame. It is a
reasoned starting point, not a measured optimum, and it is labelled as one.

WHAT IS DELIBERATELY NOT TRIED HERE. The per-net guidance window -- running the
board net only for the early denoise -- is the SECOND lever the parent named,
and it needs a driver change (diffusers takes lists for
control_guidance_start/end and broadcasts scalars only when they are not
lists). It is not taken here because this rung has one variable and this is it.
If 0.3 still damages the frame, that is the next rung and this sample is what
says so.

$0. Writes one yaml file. No GPU, no network, nothing enqueued.
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b08-boardnet-0820.yaml"
PARENT_ID = "ep2-b08-boardnet-0820"
NEW_ID = "ep2-b08-scale30-0820"
OUT = "pipeline/jobs/%s.yaml" % NEW_ID

STAGE = r"C:\banyan-farm\b08scale30-0820\src"
REPO_COMMIT = "ee74ac0e3eaf920fc7637fa7e4f2727af7684628"

TWINS_DIR = r"C:\banyan-farm\cnet-openpose-twins"
SCRIBBLE = "xinsir/controlnet-scribble-sdxl-1.0"
POSE_HINT = "pipeline/control/b08-openpose-nat-0819.png"
POSE_SHA = "562911c8174a6ecc21bc8710a1ac1b7f965c3f2d865093a742c2598c37d952e0"
BOARD_HINT = "pipeline/control/b08-board-0820.png"
BOARD_SHA = "38cd39da304dbb0317aa2522e1ccca099bef583e88e6573fde03b287358213d6"
REF_GOBLIN = "pipeline/control/b08-ref-goblin-0819.png"
REF_GUARD = "pipeline/control/b08-ref-guard-0819.png"

OLD_SCALE2 = "0.8"
NEW_SCALE2 = "0.3"


def main() -> int:
    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "beat 08 staging lane, 2026-08-20 -- derived by "
                     "pipeline/derive_b08_scale30_0820.py, on the next rung "
                     "its own parent's verdict named.",
            "consumer":
                "Beat 08's plate. The parent proved a second ControlNet CAN "
                "put the clipboard in the frame and proved the price at scale "
                "0.8 is unacceptable -- a bald guard in a shapeless robe with "
                "one arm. The cut needs to know whether the board survives at "
                "a strength that leaves the drawing alone, because that is the "
                "difference between beat 08 having a complete plate and beat "
                "08 keeping the boardless parent it already has.",
            "success":
                "One 832x1216 png with its sidecar, published to "
                "C:\\banyan-farm\\courier-box\\farm-out\\ep2-b08-scale30-0820 "
                "with a sha256 manifest, and read at 1:1 and 3x beside BOTH "
                "predecessors -- ep2-b08-twinsipa-0819, which has the drawing "
                "and no board, and ep2-b08-boardnet-0820, which has the board "
                "and not the drawing. This rung is asking for one frame with "
                "both. The preflight must print its three verification lines "
                "and the sidecar must read "
                "`controlnet_2_conditioning_scale: 0.3`.",
            "why":
                "One number, one sample, and both outcomes are informative. "
                "The mechanism is proven and cheap: every weight is on the "
                "card, both hints are byte-identical to frames already "
                "rendered, and the parent took 35 seconds end to end. If the "
                "board survives at 0.3 with the drawing intact, beat 08 has "
                "its plate recipe. If it does not, the answer is a guidance "
                "window rather than a scale, and this sample is what "
                "distinguishes them.",
        },
        overrides={
            "argv:--arm": "scale30",
            "argv:--scale2": NEW_SCALE2,
            "argv:--repo-commit": REPO_COMMIT,
        },
        retoken=[("b08boardnet-0820", "b08scale30-0820"),
                 ("ep2-b08-boardnet-0820-boardnet",
                  "ep2-b08-scale30-0820-scale30"),
                 (PARENT_ID, NEW_ID)],
        by="pipeline/derive_b08_scale30_0820.py",
        extra={
            "bar": {
                "b0_the_stack_is_what_it_claims":
                    "VOID-CHECK, unchanged from the parent except the one "
                    "number. Preflight prints `twins net verified`, `scribble "
                    "net verified`, the line asserting the two nets share size "
                    "and config and DIFFER in weights, and `staged driver, "
                    "BOTH hints and BOTH references verified`. The sidecar "
                    "must read `controlnet_2_conditioning_scale: 0.3` -- if it "
                    "reads 0.8 the override did not take and the frame is a "
                    "re-run of the parent, not a result.",
                "b4a_board_down":
                    "THE CLAUSE THIS ROUTE IS TRYING TO CLOSE. A flat board or "
                    "clipboard legibly drawn at the authored quad -- corners "
                    "(608.6,660.5) (719.5,678.1) (697.7,816.2) (586.7,798.6), "
                    "bbox x 583-723 y 657-820 -- with its top edge below the "
                    "shoulder line y=491. The parent DELIVERED this at 0.8, so "
                    "presence is not in doubt; what is in doubt is whether it "
                    "survives at 0.3. AND THE HALF THE PARENT MISSED IS SCORED "
                    "HERE: the board must be HELD. The parent's board hung "
                    "like a satchel because the far arm was absorbed into the "
                    "robe; a hand, or at minimum a lowered far arm reaching "
                    "it, is required for `the clipboard comes DOWN` to be the "
                    "picture the beat asks for. Scored by eye at 1:1 and 3x; "
                    "the edge metric is NOT used, see below.",
                "b6_drawn_not_traced":
                    "THE CLAUSE THE PARENT BROKE, AND HALF THE POINT OF THIS "
                    "RUNG. Both figures read as DRAWN CHARACTERS at "
                    "ep2-b08-twinsipa-0819's standard, which is the reference: "
                    "a face with pupils and a set jaw, hair with strands, "
                    "folds in both garments, a legible metal clasp, a drawn "
                    "hand with a dark cuff. The parent gave all of that back "
                    "for one flat robe. PASSES ONLY IF the drawing is at "
                    "twinsipa's level, not merely better than boardnet's -- "
                    "'less bad than the frame we rejected' is not a bar.",
                "b8_the_guard_has_hair":
                    "THE OTHER CLAUSE THE PARENT BROKE. canon.yaml "
                    "`ep2-guard-hair`: guard B has light sandy hair, and "
                    "\\bbald\\b is FORBIDDEN. The prompt says `light sandy "
                    "hair` and is byte-identical across all three frames. "
                    "twinsipa came back correctly haired; boardnet came back "
                    "BALD, flipping toward the reference, which is bald by "
                    "construction. PASSES IF the guard has hair. This is the "
                    "cheapest available read on whether conditioning pressure "
                    "is back to a sane level -- it moved once, so it is an "
                    "instrument now.",
                "b4b_both_arms_stay_on_their_skeletons":
                    "BOTH HALVES, AND THE SECOND HALF IS WHY IT IS RESTATED. "
                    "B4b-i: the pointing hand's centroid within ~60 px of the "
                    "authored wrist (280.5,695.1) -- twinsipa measured 40.3, "
                    "boardnet 10.2, so this has never failed and is not the "
                    "worry. B4b-ii: THE GUARD MUST HAVE TWO ARMS. boardnet's "
                    "far arm was swallowed by the robe entirely -- no elbow, "
                    "no wrist, no hand. An arm that disappears has not stayed "
                    "on its skeleton, and it is also why nothing held the "
                    "board. The goblin's arms hang and the hands do not clasp.",
                "b7_no_limb_fragmentation":
                    "CARRIED, WITH THE ADMISSIBILITY RULE THAT MADE IT "
                    "UNSCORABLE LAST TIME. G-R at six regions, three per "
                    "figure, each box ON THE DRAWN LIMB with its coordinates "
                    "AND ITS LUMA published. Within-figure spread <= 25.0; "
                    "every guard region <= 0.0, every goblin region >= +20.0. "
                    "THE PROBES MUST BE LUMA-MATCHED. On boardnet no matched "
                    "set existed -- the brightest available patch on each "
                    "guard region still spanned 120.2 luma levels because the "
                    "light had turned hard and directional -- and the clause "
                    "was reported UNMEASURABLE rather than scored. If that "
                    "happens again it is reported again, and the RECURRENCE is "
                    "itself the finding: it would mean the lighting change "
                    "tracks the second net at any strength.",
                "b2_the_identities_separate":
                    "Guard face <= 0.0, goblin face >= +20.0, separation >= "
                    "+20.0. twinsipa +42.0. Scored to catch the identities "
                    "being dragged together, and subject to the same "
                    "luma-matching condition as B7.",
                "b4c_the_arm_belongs_to_the_guard":
                    "MUST SURVIVE. The pointing arm grows from the guard's "
                    "shoulder and is human-skinned. Eight mechanisms have held "
                    "it, including boardnet.",
                "b1_the_pair":
                    "TWO figures and only two, both whole. Two is correct "
                    "under figure_count_ruled_from_the_script_0817.",
                "b3_one_ground_plane":
                    "Both stand on the same grass. twinsipa measured 4 px "
                    "between the two lowest skin rows. Read by eye if the "
                    "automated detector is confounded by foreground grass, as "
                    "it was on boardnet -- an honest eye call beats a number "
                    "from a confounded detector.",
                "b5_no_colossus":
                    "Neither figure towers. twinsipa measured a stature ratio "
                    "near 1.13 against the authored 1.100. Note that BULK is "
                    "scored under B6, not here: boardnet's guard was roughly "
                    "twice as wide and that is a drawing failure, not a "
                    "stature one.",
            },
            "not_done_on_purpose":
                "ONE sample, ONE arm, ONE number. No sweep -- 0.3 is a single "
                "reasoned value and if it is wrong the next sample moves it "
                "once more. No per-net guidance window, which is the SECOND "
                "lever the parent named and needs its own driver change and "
                "its own rung. No change to either hint (both byte-identical), "
                "no change to the masks, the references, the ip-scale, the "
                "first net's scale, the seed or a single word of the prompt. "
                "No third figure. No colour-cast fix. No pick, no plate_ack, "
                "no canon filename, no canon.yaml edit.",
            "the_number_is_reasoned_not_measured":
                "SAID PLAINLY SO NOBODY LATER CITES 0.3 AS AN OPTIMUM. The "
                "parent ran the two nets at 1.0 + 0.8 = 1.8 total conditioning "
                "and the frame flattened everywhere. Beat 08 has rendered well "
                "at a single net at 1.0 and at 0.8. 0.3 puts the sum at 1.3 -- "
                "above what has worked, below what failed, and closer to the "
                "former. That is an argument, not a measurement, and this "
                "sample is the measurement.",
            "rights_and_weights":
                "THIS IS THE `licence_note`. Unchanged from the parent and "
                "clean. Base cagliostrolab/animagine-xl-3.1 (CreativeML Open "
                "RAIL++-M). Net 1 xinsir/controlnet-openpose-sdxl-1.0 twins "
                "variant, apache-2.0. Net 2 xinsir/controlnet-scribble-sdxl-"
                "1.0, apache-2.0, no attribution condition. IP-Adapter "
                "h94/IP-Adapter, apache-2.0. Both references are repo-internal "
                "crops. BOTH hints are authored in PIL from numbers -- no "
                "annotator, so the lllyasviel/Annotators landmine is untouched "
                "by either condition. MistoLine is not used.",
            "scoring_rule_pre_registered":
                "THIS IS THE `verdict_rule`, WRITTEN BEFORE THE PIXELS.\n"
                "(1) BOARD PRESENT AND HELD, AND B6 + B8 AT twinsipa's LEVEL, "
                "AND THE CARRIED CLAUSES SURVIVE -> PASS, and beat 08 has a "
                "COMPLETE plate candidate for the first time. Still NOT a pick "
                "and NOT a plate_ack; that is R4's call.\n"
                "(2) BOARD PRESENT, B6 AND B8 RECOVERED, BUT THE BOARD IS HUNG "
                "RATHER THAN HELD -> the strength question is SETTLED and the "
                "remaining question is the arm. Next rung is wording or a hint "
                "that includes the forearm reaching the board, NOT another "
                "scale.\n"
                "(3) BOARD GONE AND THE DRAWING RECOVERED -> 0.3 is below this "
                "hint's threshold. The board lives in a window between 0.3 and "
                "0.8 and the next sample takes the midpoint; the mechanism is "
                "confirmed either way.\n"
                "(4) BOARD PRESENT AND THE DRAWING STILL DAMAGED -> scale is "
                "NOT the lever. The damage is not proportional to strength, "
                "which points at the full-denoise application rather than the "
                "magnitude, and the next rung is the per-net guidance window.\n"
                "(5) B7 UNMEASURABLE AGAIN for the same lighting reason -> the "
                "hard directional key travels with the second net at any "
                "strength, which is a finding about the net and not about this "
                "frame, and it changes what the route is willing to spend a "
                "second condition on at all.",
            "who_ruled_this_rung":
                "ep2-b08-boardnet-0820's own verdict, under "
                "`next_rung_named_not_taken`: \"ONE sample, and the variable "
                "is the SECOND NET'S STRENGTH, nothing else... with --scale2 "
                "dropped from 0.8 to about 0.3. Its bar is B4a AND the two "
                "clauses this rung broke, B6 and B8, restored to parent "
                "quality.\" Fired immediately because the card was idle with "
                "nothing claimed and nothing waiting, and the job has no "
                "dependency: every weight is local and both hints already "
                "exist. Written in an `extra` key because `fresh` prose is "
                "retokened and a parent id there would become this job's own "
                "id.",
            "why_these_key_names":
                "`scoring_rule_pre_registered` and `rights_and_weights` are "
                "this spec's `verdict_rule` and `licence_note`. derive_spec's "
                "FINDINGS_NAME guard refuses any extra key matching "
                "/verdict|licen[cs]/, which is right for findings and "
                "over-reaches on two house keys that must be written BEFORE "
                "the pixels. Same declaration the last two rungs made.",
        },
    )

    # The render step's NAME is not a token retoken can reach -- it is the bare
    # word "boardnet", not the job id -- so it is renamed explicitly, the same
    # way the parent's deriver had to.
    step = [s for s in child["steps"] if s["name"] == "boardnet"][0]
    step["name"] = "scale30"

    # ---- ASSERTIONS. The parent's conditioning must be carried byte-for-byte
    # ---- and exactly ONE number may differ.
    argvs = [str(a) for s in child["steps"] for a in s["argv"]]

    def flag(n):
        return [argvs[i + 1] for i, v in enumerate(argvs) if v == n]

    assert flag("--scale2") == [NEW_SCALE2], flag("--scale2")
    assert OLD_SCALE2 not in flag("--scale2"), "the old scale survived"
    assert flag("--scale") == ["1.0"], flag("--scale")
    assert flag("--controlnet") == [TWINS_DIR]
    assert flag("--controlnet2") == [SCRIBBLE]
    assert flag("--control") == [POSE_HINT]
    assert flag("--control-sha256") == [POSE_SHA]
    assert flag("--control2") == [BOARD_HINT]
    assert flag("--control2-sha256") == [BOARD_SHA]
    assert flag("--seed") == ["20260819"], flag("--seed")
    assert flag("--ip-ref") == [REF_GOBLIN, REF_GUARD]
    assert flag("--ip-scale") == ["0.7"]
    assert len(flag("--ip-mask-capsules")) == 2
    assert flag("--arm") == ["scale30"], flag("--arm")
    assert flag("--root") == [STAGE], flag("--root")
    assert [s["name"] for s in child["steps"]] == ["preflight", "scale30",
                                                   "publish"]

    runnable = "\n".join(argvs + list(child.get("payload") or {})
                         + [str(x) for x in (child.get("artifacts") or [])])
    assert PARENT_ID not in runnable, "the parent id survived a runnable path"

    # the words did not move, across THREE frames now
    import yaml as _yaml
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    parent = _yaml.safe_load(open(os.path.join(root, PARENT), encoding="utf-8"))
    pp = {os.path.basename(k.replace("\\", "/")): v
          for k, v in parent["payload"].items()}
    cp = {os.path.basename(k.replace("\\", "/")): v
          for k, v in child["payload"].items()}
    assert pp == cp, "payload text drifted from the parent's"
    assert "light sandy hair" in cp["prompt.txt"]
    assert "bald" not in cp["prompt.txt"], "canon ep2-guard-hair forbids bald"

    # and both hints on disk are still the bytes this spec pins
    for rel, want in ((BOARD_HINT, BOARD_SHA), (POSE_HINT, POSE_SHA)):
        with open(os.path.join(root, rel), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        assert got == want, "%s is %s, spec pins %s" % (rel, got, want)

    out = derive_spec.write(child, OUT)
    print("wrote %s" % out)
    print("id        %s" % child["id"])
    print("parent    %s" % PARENT_ID)
    print("variable  --scale2 %s -> %s (nothing else)" % (OLD_SCALE2, NEW_SCALE2))
    print("steps     %s" % " -> ".join(s["name"] for s in child["steps"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
