#!/usr/bin/env python3
r"""Derive `ep2-b08-gripmark-0820` FROM `ep2-b08-scale30-0820`.

THE ONE VARIABLE: the board hint. `pipeline/control/b08-board-0820.png` ->
`pipeline/control/b08-board-grip-0820.png`, which is the same file plus ONE
closed hand-sized loop at the authored guard L-wrist. Nothing else moves. The
prompt is the parent's 64-token text, byte-identical (asserted), which means
this rung also takes back the nine words that cost the hair and the board at
section 18. Both nets, `--scale` 1.0, `--scale2` 0.3, the capsule masks, the
references, the ip-scale, the openpose hint (562911c8) and the seed (20260819)
are all the parent's.

WHY THIS IS AUTHORISED AND WHY IT IS NOT THE THING THREE RUNGS KEPT NAMING.
Sections 17, 18 and 19 each ended by naming "a SHORT STROKE for the gripping
hand" and each added that it was owed the five scribble-net tracing losses in
writing first. That writing is now filed --
`pipeline/work-ladder-0819.md`, "the grip mark, argued against the five tracing
losses" -- and it REJECTS the proposal as named. A short stroke is tracing loss
4 exactly: r4's 1 px finger, appended to the end of a limb at a HIGHER strength
with a whole contour around it to hold it, did not carry and cost r2's
articulated hand a fingerless wedge. Section 9 ruled on it at the time: "whatever
the class, B4b needs a HAND-SIZED mark at the end of the arm."

WHAT SURVIVED THE FIVE LOSSES, IN ONE PARAGRAPH. A closed loop is ENCLOSURE
class, which is the one thing a scribble net reads, and the positive control is
not an argument but this very frame: the same net, the same hint file, the same
0.3, the same seed already put a closed quad on screen at the authored position
and the authored 9-degree tilt. It is drawn at 7 px because section 9 measured
stroke as a PRECISION dial with the opposite sign to the assumption -- 3 px is a
single unambiguous edge locus and the outline snaps to it, 7 px is an ambiguous
ribbon the model fills with its own drawing, which is why r2, at 7 px, is the ONE
frame in the five losses that produced a good articulated hand at an enclosed arm
terminus. Its scope is one body part and 0.31% of the frame; losses 1-4
conditioned the entire silhouette of two whole bodies and what they cost was
CHARACTER -- identity, wardrobe, linework, face -- and this loop is silent on all
four. And section 16's "a black pixel means NO EDGE HERE" objection, which would
predict the loop commissioning a flat mitten, is answered by the parent's own B6
verdict: at 0.3 that same nearly-black hint left the model free enough to draw
"a well-drawn fist gripping the harness strap with individual fingers."

ONE MEASUREMENT THAT RE-DESCRIBES THE DEFECT, taken off the parent frame with
geometry-placed boxes. The guard's near hand is not missing and is not badly
drawn: its centroid is (620.3, 577.9), which is 7.1 px from the authored ELBOW
(627.2, 579.7) and 90.5 px from the authored WRIST (621.6704, 668.4352). The arm
is drawn one joint short and 90 px of sleeve fabric fills the rest, terminating
in a digit-free lobe at (679.2, 630.4) on the board's top edge. So this rung is
not asking the object net for a DRAWING -- which the five losses say it will not
give -- it is asking for a POSITION, at a coordinate the pose net has authored
since 562911c8 and section 14 already showed the checkpoint willing to override.

$0. Writes one yaml file. No GPU, no network, nothing enqueued.
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import clip_token_count  # noqa: E402
import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b08-scale30-0820.yaml"
PARENT_ID = "ep2-b08-scale30-0820"
NEW_ID = "ep2-b08-gripmark-0820"
OUT = "pipeline/jobs/%s.yaml" % NEW_ID

STAGE = r"C:\banyan-farm\b08gripmark-0820\src"
# The commit that carries the grip hint and the --grip flag that drew it.
REPO_COMMIT = "8b7dd6beb8f922f6ba8b6da81833b8a2acb2b6d7"

TWINS_DIR = r"C:\banyan-farm\cnet-openpose-twins"
SCRIBBLE = "xinsir/controlnet-scribble-sdxl-1.0"
DRIVER = "pipeline/controlnet_plate.py"
DRIVER_SHA = "aff188907fa03914b30a8cec2e5f739a5c4941f5d4246f4b2e220a9cc047c66a"
POSE_HINT = "pipeline/control/b08-openpose-nat-0819.png"
POSE_SHA = "562911c8174a6ecc21bc8710a1ac1b7f965c3f2d865093a742c2598c37d952e0"
OLD_BOARD_HINT = "pipeline/control/b08-board-0820.png"
OLD_BOARD_SHA = "38cd39da304dbb0317aa2522e1ccca099bef583e88e6573fde03b287358213d6"
NEW_BOARD_HINT = "pipeline/control/b08-board-grip-0820.png"
NEW_BOARD_SHA = "e822a88a6cfb82a805c2c417c315f3cc0f0f2d2e963720694fb9400897353f63"
REF_GOBLIN = "pipeline/control/b08-ref-goblin-0819.png"
REF_GOBLIN_SHA = "13b0c69d2f95dad6fd5472d8ab0310967b1a88c4554de7e6ff74b2d3e3644d8c"
REF_GUARD = "pipeline/control/b08-ref-guard-0819.png"
REF_GUARD_SHA = "61dc3f7fbd052617e52db63e8f6d359822b6ceba14b13514ffc03179b56cd83c"

SEED = 20260819
SCALE2 = "0.3"
LWRI = (621.6704, 668.4352)


def main() -> int:
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    # ---- THE HINT IS THE VARIABLE, SO ITS PIXELS ARE CHECKED HERE, NOT
    # TRUSTED. Re-derive both variants in memory from the author module and
    # assert the filed PNGs are exactly them. A spec that pins a sha nobody
    # re-derived is pinning a file, not a hint.
    import io
    import author_b08_board_hint as bh
    for grip, rel, want in ((False, OLD_BOARD_HINT, OLD_BOARD_SHA),
                            (True, NEW_BOARD_HINT, NEW_BOARD_SHA)):
        buf = io.BytesIO()
        bh.build(grip=grip)[0].save(buf, "PNG")
        got = hashlib.sha256(buf.getvalue()).hexdigest()
        assert got == want, "build(grip=%s) is %s, spec pins %s" % (
            grip, got, want)
    g = bh.board_geometry()
    assert abs(g["grip"][0] - LWRI[0]) < 1e-9 \
        and abs(g["grip"][1] - LWRI[1]) < 1e-9, g["grip"]

    import yaml as _yaml
    parent = _yaml.safe_load(open(os.path.join(root, PARENT), encoding="utf-8"))
    ppay = {os.path.basename(k.replace("\\", "/")): v
            for k, v in parent["payload"].items()}
    clip = clip_token_count.Clip()
    n_p, _ = clip.count(ppay["prompt.txt"])
    total = n_p + clip_token_count.SPECIALS
    assert total == 64, "the parent prompt no longer measures 64: %d" % total
    assert "fingers and thumb" not in ppay["prompt.txt"], \
        "this rung renders the 64-token text, not the grip wording"

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "beat 08 staging lane, 2026-08-20 -- derived by "
                     "pipeline/derive_b08_gripmark_0820.py, on the lever three "
                     "rungs named and none authored. The argument the record "
                     "owed is filed first, in pipeline/work-ladder-0819.md, and "
                     "it changed the proposal from a stroke to a closed loop. "
                     "Fired without waiting for a human hour: every weight is "
                     "on the card, both hints exist, and the previous rungs "
                     "took ~30 s of GPU end to end.",
            "consumer":
                "Beat 08's plate, and this is the last named lever on it. The "
                "beat asks for a clipboard LOWERED IN ONE HAND. The best frame "
                "the beat has draws the board correctly and ends the sleeve in "
                "a digit-free lobe on its top edge, with the hand itself 90.5 "
                "px away at the elbow gripping a strap the model invented. The "
                "cut cannot use a board that reads as a satchel, and every "
                "input that does not require figure ink has now been spent: "
                "wording summons a grip and binds it to the wrong object while "
                "costing the board, strength restores the board and moves no "
                "hand while merging the wardrobe, and the guidance window was "
                "excluded two rungs earlier.",
            "success":
                "One 832x1216 png with its sidecar, published to "
                "C:\\banyan-farm\\courier-box\\farm-out\\ep2-b08-gripmark-0820 "
                "with a sha256 manifest, and read at 1:1, 3x AND 5x beside its "
                "parent -- 5x because that is the magnification at which the "
                "parent's lobe was found to have no digits, and a grip judged "
                "at 1:1 is a grip not judged. The preflight must print its four "
                "verification lines; the sidecar must read "
                "`control_2_image_sha256: e822a88a...`, "
                "`controlnet_2_conditioning_scale: 0.3`, "
                "`controlnet_conditioning_scale: 1.0`, "
                "`control_image_sha256: 562911c8...` and `seed: 20260819`; and "
                "its `prompt:` must NOT contain `fingers and thumb`.",
            "why":
                "One sample, one variable, ~30 s of GPU, and the record already "
                "predicts what each outcome means because the five failure "
                "modes were written down before the hint was drawn. A hand at "
                "the board closes beat 08's last clause. No hand at all says "
                "small-scope figure ink cannot bind at the only strength the "
                "wardrobe survives, which sends the beat to the "
                "composite-then-inpaint route that went 4 for 4 today -- and "
                "that is worth knowing before anyone spends a second GPU hour "
                "on this net.",
        },
        overrides={
            "argv:--arm": "gripmark",
            "argv:--control2": NEW_BOARD_HINT,
            "argv:--control2-sha256": NEW_BOARD_SHA,
            "argv:--repo-commit": REPO_COMMIT,
            "seed": SEED,
        },
        retoken=[("b08scale30-0820", "b08gripmark-0820"),
                 ("ep2-b08-scale30-0820-scale30",
                  "ep2-b08-gripmark-0820-gripmark"),
                 # the preflight's staged-file table and the publish step's
                 # glob both name the hint by filename and by sha.
                 ("b08-board-0820.png", "b08-board-grip-0820.png"),
                 (OLD_BOARD_SHA, NEW_BOARD_SHA)],
        by="pipeline/derive_b08_gripmark_0820.py",
        extra={
            "bar": {
                "b0_the_stack_is_what_it_claims":
                    "VOID-CHECK, and it has one MORE line to read than the "
                    "parent's because the variable is a conditioning input "
                    "rather than a number. Preflight prints `twins net "
                    "verified`, `scribble net verified`, the line asserting the "
                    "two nets share size and config and DIFFER in weights, and "
                    "`staged driver, BOTH hints and BOTH references verified` "
                    "-- and the staged-file table now pins "
                    "b08-board-grip-0820.png at e822a88a..., so a stale hint on "
                    "the box fails here rather than in a verdict. The sidecar "
                    "must read control_2_image_sha256 e822a88a... and "
                    "control_image_sha256 562911c8...: if the second reads "
                    "38cd39da... the new hint never reached the card and the "
                    "frame is a re-run of the parent under a new name.",
                "b4b_the_grip":
                    "THE CLAUSE THIS RUNG EXISTS FOR, AND IT IS SCORED AT 5x. "
                    "A HAND at the board's top edge: a form that reads as a "
                    "hand, whose centroid is CLOSER TO THE AUTHORED WRIST "
                    "(621.7, 668.4) THAN TO THE AUTHORED ELBOW (627.2, 579.7) "
                    "-- i.e. under ~45 px from the wrist, against the parent's "
                    "90.5 -- and which overlaps the board's top edge rather "
                    "than hovering above it or sitting behind it. Digits are "
                    "scored SEPARATELY and are not required for the clause to "
                    "pass: the beat asks for a clipboard held, not for a hand "
                    "anatomy study, and the parent already proves the model "
                    "draws digits at 0.3 when it decides a hand is a hand. "
                    "Placed by geometry, not by colour -- a colour predicate "
                    "cannot certify skin on this guard, whose cream shirt reads "
                    "R-B 34.7 against his skin's 42.6-49.7.",
                "b4a_board_down":
                    "MUST NOT REGRESS, AND THIS IS NOT A FORMALITY. Section 18 "
                    "established that --scale2 0.3 is not robust but "
                    "PROMPT-COUPLED: it carried the board for exactly the text "
                    "it was measured with and lost it entirely for nine more "
                    "words at the same strength. This rung moves the OTHER half "
                    "of that pair, so the object is re-measured by the same "
                    "instrument: fraction of pixels below luma 80 inside the "
                    "authored quad -- corners (608.6,660.5) (719.5,678.1) "
                    "(697.7,816.2) (586.7,798.6) -- published for BOTH frames "
                    "computed the same way in the same pass, because the "
                    "published 0.758/0.235 figures came from an instrument this "
                    "lane cannot reproduce exactly. Top edge below the shoulder "
                    "line y=491, one board and only one.",
                "b6_drawn_not_traced":
                    "THE CLAUSE THE FIVE TRACING LOSSES ARE ABOUT, AND THE "
                    "REASON THE ARGUMENT HAD TO BE WRITTEN FIRST. Both figures "
                    "read as DRAWN CHARACTERS at ep2-b08-twinsipa-0819's "
                    "standard: pupils and a set jaw, hair with strands, folds "
                    "in BOTH garments -- cream shirt, white sash AND brown wrap "
                    "as three separable things -- a legible metal clasp, a "
                    "drawn cuff. SPECIFICALLY: the guard's face must not be "
                    "traced, and nothing anywhere in the frame may read as a "
                    "hard-rimmed flat form. A flat blob at the wrist is fail "
                    "mode L2 and is scored as a FAIL of this clause, not as a "
                    "partial win on B4b.",
                "b8_the_guard_has_hair":
                    "canon.yaml `ep2-guard-hair` -- light sandy hair, \\bbald\\b "
                    "FORBIDDEN, and beat 08 is in that entry's scope as of "
                    "2026-08-20. THE INSTRUMENT HAS TWO CALIBRATED INPUTS AND "
                    "THIS RUNG HOLDS BOTH AT THE VALUES THAT PASSED: 64 tokens "
                    "(bald arrived at 73) and 1.0+0.3 (bald arrived at 1.0+0.8 "
                    "and 1.0+0.5). So a bald guard here would mean the loop "
                    "itself raised the effective load, which is a third input "
                    "nobody has measured and would be the finding of the rung.",
                "b7_no_limb_fragmentation":
                    "G-R at six regions, three per figure, EVERY BOX PLACED "
                    "FRESH ON THIS FRAME and publishing coordinates, luma AND "
                    "material. Within-figure spread <= 25.0; every guard region "
                    "<= 0.0, every goblin region >= +20.0. Two standing "
                    "admissibility rules, both earned on this beat: boxes do "
                    "not transfer between frames because wardrobe moves under "
                    "them, and ON THE GUARD A COLOUR PREDICATE CANNOT DECIDE "
                    "THE MATERIAL. Guard boxes are placed by eye at 5x and "
                    "published with their R-B.",
                "b2_the_identities_separate":
                    "Guard face <= 0.0, goblin face >= +20.0, separation >= "
                    "+20.0. twinsipa +42.0, the parent +60.6. Same "
                    "material-and-luma publication rule as B7.",
                "b4b_ii_both_arms_stay_on_their_skeletons":
                    "The pointing hand's centroid within ~60 px of the authored "
                    "wrist (280.5,695.1) -- parent 48.5 -- and THE GUARD MUST "
                    "HAVE TWO ARMS, neither swallowed. The pointing arm is the "
                    "clause the loop is furthest from and the hint's selftest "
                    "asserts it is not touched; if it moves, the loop is acting "
                    "globally and that is fail mode L2 in a worse form.",
                "b4c_the_arm_belongs_to_the_guard":
                    "MUST SURVIVE. The pointing arm grows from the guard's "
                    "shoulder and is human-skinned. Eleven mechanisms have held "
                    "it.",
                "b1_the_pair":
                    "TWO figures and only two, both whole, under "
                    "figure_count_ruled_from_the_script_0817. AND EXACTLY ONE "
                    "BOARD and TWO HANDS ON THE GUARD -- fail mode L5 is a hand "
                    "at the wrist ARRIVING ALONGSIDE the existing fist at the "
                    "strap, which would be three hand-forms on one man.",
                "b3_one_ground_plane":
                    "Both stand on the same grass. Read by eye if the automated "
                    "detector is confounded by foreground grass, as it has been "
                    "on the last two frames.",
                "b5_no_colossus":
                    "Neither figure towers; twinsipa measured a stature ratio "
                    "near 1.13 against the authored 1.100.",
            },
            "the_argument_this_rung_required_before_it_could_exist":
                "FILED FIRST, IN pipeline/work-ladder-0819.md -- \"the grip "
                "mark, argued against the five tracing losses\". Read it before "
                "reading this spec's result, because it also REJECTS the lever "
                "as three rungs named it. The proposal on the record was \"a "
                "SHORT STROKE for the gripping hand\"; a short stroke is "
                "tracing loss 4 exactly (r4's 1 px finger at 0.45, which did "
                "not carry and cost r2's articulated hand a fingerless wedge), "
                "and section 9 ruled at the time that what B4b needs is a "
                "HAND-SIZED mark. What is authored here is a CLOSED LOOP, and "
                "author_b08_board_hint.py --selftest proves the word closed "
                "with a flood fill seeded off-ink at its centre that must be "
                "trapped, the way section 10 proved the contour/skeleton "
                "distinction.",
            "one_variable_and_how_it_is_proved":
                "NOT BY PROMISE. build(grip=False) is still the default and "
                "--selftest asserts it is byte-identical to 38cd39da..., the "
                "hint four rungs rendered from, both re-derived in memory and "
                "on disk; the grip hint is asserted a strict SUPERSET of it, "
                "with every added pixel inside the loop's own dilation. The two "
                "hints therefore differ by the loop and by nothing else, as a "
                "measurement. The prompt is the parent's payload dict, "
                "byte-identical, asserted equal in this deriver and measured at "
                "64 of 77 tokens. Both nets, both shas, both capsule masks, the "
                "openpose hint, --scale, --scale2, --ip-scale and the seed are "
                "the parent's untouched.",
            "pre_registered_fail_modes":
                "WRITTEN BEFORE THE PIXELS, EACH TIED TO THE LOSS IT COMES "
                "FROM.\n"
                "L1 IGNORED (loss 3 class, AND THE MOST LIKELY): the hand stays "
                "at the elbow and the board is unchanged. At 0.28 figure ink "
                "stopped binding entirely and this loop carries about a tenth "
                "of the board's ink at 0.3. Reads as: small-scope figure ink "
                "cannot bind at the only strength the wardrobe survives, and "
                "the route leaves this net.\n"
                "L2 FLAT-TRACE (loss 1 class): a hard-rimmed digit-free blob at "
                "the wrist. Reads as: 7 px is not a ribbon at 0.3, i.e. section "
                "9's precision finding is scale-dependent. Scored a FAIL of B6, "
                "not a partial B4b.\n"
                "L3 MERGE (loss 5 class): the loop's ink and the board's top "
                "edge read as ONE enclosure -- a bump on the board, or a "
                "luminous bar at the wrist. The loop straddles the edge by "
                "design and this is the price of that design.\n"
                "L4 BOARD-COST (section 18 class): the board degrades or "
                "vanishes because the PAIR moved. Section 18's lesson was "
                "written for prompt edits at a fixed hint; this is a hint edit "
                "at a fixed prompt and the same logic applies. Measured, not "
                "eyeballed.\n"
                "L5 THIRD-HAND: a hand at the wrist arrives ALONGSIDE the "
                "existing fist at the strap. `extra hands` is in the negative "
                "and negatives have not been reliable on this beat.\n"
                "A frame can fire more than one; section 18 fired two at once.",
            "the_fallback_named_in_advance":
                "COMPOSITE-THEN-INPAINT, and it is named now so nobody has to "
                "invent an instrument after a disappointment. That route went 4 "
                "for 4 on 2026-08-20 (beats 15, 19, 03, 13) on precisely this "
                "shape of problem -- a RELATION between a figure the sampler has "
                "already placed and something it draws where it likes. Beat 03's "
                "entry states the general form: a relation is no more a knob "
                "than a numeral is. \"A hand grips this board\" is that "
                "relation. Drawing the hand into the parent plate and running a "
                "0.30 pass with padding_mask_crop=64 touches neither net and "
                "risks neither the board nor the wardrobe. The hint rung goes "
                "first only because it is one variable on a recipe already on "
                "the card and keeps beat 08's plate a single-pass render.",
            "not_done_on_purpose":
                "ONE sample, ONE arm, ONE hint. NO second seed. NO scale sweep "
                "-- section 19 closed the number and the window is narrower "
                "than 0.3-0.5. NO wording change in either direction beyond "
                "reverting to the parent's own 64-token payload, which is not a "
                "change but the absence of one. NO knuckles, NO thumb, NO "
                "finger divisions in the loop: r2's hand was good and aimed "
                "wide BY CONSTRUCTION, and hand-authored geometry fails by "
                "being confidently wrong. NO second mark anywhere in the hint "
                "and NO new limb in its contact set, both asserted as pixels. "
                "NO change to the openpose hint, the masks, the references, the "
                "ip-scale, the first net's scale or the driver. NO pick, NO "
                "plate_ack, NO cut, NO canon filename, NO canon.yaml edit.",
            "rights_and_weights":
                "THIS IS THE `licence_note`. Unchanged and clean. Base "
                "cagliostrolab/animagine-xl-3.1 (CreativeML Open RAIL++-M). Net "
                "1 xinsir/controlnet-openpose-sdxl-1.0 twins variant, "
                "apache-2.0. Net 2 xinsir/controlnet-scribble-sdxl-1.0, "
                "apache-2.0, no attribution condition. IP-Adapter "
                "h94/IP-Adapter, apache-2.0. Both references are repo-internal "
                "crops. BOTH hints are authored in PIL from numbers -- no "
                "annotator, so the lllyasviel/Annotators landmine is untouched "
                "by either condition, and that remains true of the grip loop, "
                "which is eight vertices of arithmetic.",
            "scoring_rule_pre_registered":
                "THIS IS THE `verdict_rule`, WRITTEN BEFORE THE PIXELS.\n"
                "(1) A HAND AT THE BOARD, EVERY PARENT CLAUSE HELD -> beat 08 "
                "has a COMPLETE plate candidate for the first time and the "
                "route stops. Pixels get staged for cut assembly and said so "
                "plainly. STILL NOT a pick and NOT a plate_ack -- choosing "
                "between frames is taste and belongs to R4.\n"
                "(2) A HAND AT THE BOARD, A PARENT CLAUSE LOST -> the loop acts "
                "globally as well as locally, which is the five losses "
                "re-appearing at small scope. Not a candidate; the finding is "
                "that scope does not buy locality on this net.\n"
                "(3) NO CHANGE AT ALL (L1) -> figure ink at 0.3 is below "
                "threshold. The scribble net is spent as a placement "
                "instrument on this beat and the route goes to the composite.\n"
                "(4) THE BOARD DEGRADES (L4) -> section 18's coupling is a "
                "property of the pair in BOTH directions, which constrains "
                "every future multi-net beat, not just this one.\n"
                "(5) A THIRD HAND-FORM (L5) -> the checkpoint adds hands rather "
                "than relocating them, and no hint-side instrument can fix a "
                "hand that is already committed elsewhere. That is the cleanest "
                "possible licence for the composite route.",
            "who_ruled_this_rung":
                "The parent's own verdict under `next_rung_named_not_taken` "
                "(\"IF WORDING FAILS, the next lever is the board hint carrying "
                "a short stroke for the gripping hand at the authored L-wrist "
                "-- which would be the first figure ink ever put in that hint "
                "and must be argued for explicitly against the five tracing "
                "losses, not slipped in\"), and route log "
                "pipeline/b08-arm-route-0819.md sections 17, 18 and 19, which "
                "say the same three times. The argument is filed; the lever is "
                "taken in the class the argument survived in, which is a closed "
                "loop and not a stroke. Written in an `extra` key because "
                "`fresh` prose is retokened and a parent id there would become "
                "this job's own id.",
            "why_these_key_names":
                "`scoring_rule_pre_registered` and `rights_and_weights` are "
                "this spec's `verdict_rule` and `licence_note`. derive_spec's "
                "FINDINGS_NAME guard refuses any extra key matching "
                "/verdict|licen[cs]/, which is right for findings and "
                "over-reaches on two house keys that must be written BEFORE the "
                "pixels. Same declaration the last five rungs made.",
        },
    )

    step = [s for s in child["steps"] if s["name"] == "scale30"][0]
    step["name"] = "gripmark"

    argvs = [str(a) for s in child["steps"] for a in s["argv"]]

    def flag(n):
        return [argvs[i + 1] for i, v in enumerate(argvs) if v == n]

    # ---- THE VARIABLE MOVED ...
    assert flag("--control2") == [NEW_BOARD_HINT], flag("--control2")
    assert flag("--control2-sha256") == [NEW_BOARD_SHA], flag("--control2-sha256")
    # ---- ... AND NOTHING ELSE DID.
    assert flag("--scale2") == [SCALE2], flag("--scale2")
    assert flag("--scale") == ["1.0"], flag("--scale")
    assert flag("--seed") == [str(SEED)], flag("--seed")
    assert flag("--controlnet") == [TWINS_DIR]
    assert flag("--controlnet2") == [SCRIBBLE]
    assert flag("--control") == [POSE_HINT]
    assert flag("--control-sha256") == [POSE_SHA]
    assert flag("--ip-ref") == [REF_GOBLIN, REF_GUARD]
    assert flag("--ip-ref-sha256") == [REF_GOBLIN_SHA, REF_GUARD_SHA]
    assert flag("--ip-scale") == ["0.7"]
    assert len(flag("--ip-mask-capsules")) == 2
    assert flag("--arm") == ["gripmark"], flag("--arm")
    assert flag("--root") == [STAGE], flag("--root")
    assert flag("--repo-commit") == [REPO_COMMIT], flag("--repo-commit")
    assert [s["name"] for s in child["steps"]] == ["preflight", "gripmark",
                                                   "publish"]

    pargv = [str(a) for s in parent["steps"] for a in s["argv"]]
    assert flag("--ip-mask-capsules") == [pargv[i + 1] for i, v in
                                          enumerate(pargv)
                                          if v == "--ip-mask-capsules"], \
        "the capsule masks moved"

    # ---- THE OLD HINT IS GONE FROM EVERY CORNER OF THE SPEC, including the
    # preflight's staged-file table and the publish step's glob. A child that
    # renders the new hint but preflights the old one would verify a file it
    # does not use, which is worse than no preflight at all.
    # The `derivation` block is EXCLUDED on purpose: it lists the retoken pairs
    # and must name the old sha and the old filename, because "what changed" is
    # the one place they still belong. Everywhere else they are a bug.
    body = derive_spec._dump({k: v for k, v in child.items()
                              if k != "derivation"})
    assert OLD_BOARD_SHA not in body, "the parent hint's sha survived"
    assert "b08-board-0820.png" not in body, "the parent hint's name survived"
    assert body.count(NEW_BOARD_SHA) >= 2, \
        "the new sha must appear in the argv AND in the preflight table"
    assert POSE_SHA in body and body.count(POSE_SHA) >= 2, \
        "the openpose hint must still be pinned in both places"

    runnable = "\n".join(argvs + list(child.get("payload") or {})
                         + [str(x) for x in (child.get("artifacts") or [])])
    assert PARENT_ID not in runnable, "the parent id survived a runnable path"

    # ---- THE WORDS DID NOT MOVE.
    cpay = {os.path.basename(k.replace("\\", "/")): v
            for k, v in child["payload"].items()}
    assert cpay == ppay, "the prompt or the negative drifted from the parent's"
    assert "clipboard lowered in one hand" in cpay["prompt.txt"]
    assert "light sandy hair" in cpay["prompt.txt"]
    assert "fingers and thumb" not in cpay["prompt.txt"]
    assert "bald" not in cpay["prompt.txt"], "canon ep2-guard-hair forbids bald"

    for rel, want in ((DRIVER, DRIVER_SHA), (POSE_HINT, POSE_SHA),
                      (NEW_BOARD_HINT, NEW_BOARD_SHA),
                      (REF_GOBLIN, REF_GOBLIN_SHA), (REF_GUARD, REF_GUARD_SHA)):
        with open(os.path.join(root, rel), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        assert got == want, "%s is %s, spec pins %s" % (rel, got, want)

    out = derive_spec.write(child, OUT)
    print("wrote %s" % out)
    print("id        %s" % child["id"])
    print("parent    %s" % PARENT_ID)
    print("variable  --control2 %s -> %s" % (OLD_BOARD_HINT, NEW_BOARD_HINT))
    print("          (the same file plus ONE closed loop at %r)" % (LWRI,))
    print("prompt    %d of 77, byte-identical to the parent's" % total)
    print("held      --scale 1.0  --scale2 %s  --seed %d  openpose 562911c8..."
          % (SCALE2, SEED))
    print("steps     %s" % " -> ".join(s["name"] for s in child["steps"]))
    print("stage     %s" % STAGE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
