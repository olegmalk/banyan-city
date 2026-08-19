#!/usr/bin/env python3
r"""Derive `ep2-b08-grip-0820` FROM `ep2-b08-scale30-0820`.

THE ONE VARIABLE: NINE WORDS IN THE POSITIVE PROMPT. Nothing else moves. Same
two nets, same two hints (both byte-identical), same capsule masks, same
references, same ip-scale, both conditioning scales, same seed, same negative.

WHY, IN ONE PARAGRAPH. The parent PASSED the question it asked -- the board
survives at `--scale2` 0.3 and everything the 0.8 rung broke came back: sandy
hair against canon, cream shirt and wrap skirt, both arms, B7 on both figures,
B2 at +60.6, mean luma 135.4 against twinsipa's 141.6 -- and it came up SHORT BY
EXACTLY ONE CLAUSE. At 5x the guard's sleeve ends in a rounded mitten-like form
and the board's top edge tucks under it: no fingers, no thumb, no grip. The beat
asks for a clipboard LOWERED IN ONE HAND and what is drawn is a board carried at
the end of a sleeve. The far arm now REACHES the board -- that half is done --
so the remaining gap is the hand itself.

WHY WORDING, AND WHY FIRST. The parent's own verdict named this rung and named
this lever: "ONE sample: THE HAND ON THE BOARD, with --scale2 held at 0.3 and
the board hint held byte-identical. The cheapest lever first, because it is free
and because the wording is already half-right." Two standing laws on this route
agree. PROMPT-SUMMONS: a positively placed assertion beats a negative, and the
negative already carries `deformed hands`/`extra fingers` while the positive
asserted no hand at all. UNASSERTED ATTRIBUTES FALL TO WORDING: this is the same
shape as B8, where the guard's hair -- asserted in the prompt and nowhere else --
returned the moment conditioning pressure dropped. A grip that nothing asserts
is a grip the model is free not to draw.

WHAT THE NINE WORDS ARE, AND WHY THESE NINE.

    clipboard lowered in one hand,
    + fingers and thumb gripping the clipboard edge,

The parent's verdict names three absences in one sentence -- "no fingers, no
thumb, no grip" -- so the clause asserts all three POSITIVELY and binds them to
the object: `fingers` and `thumb` are the two nouns, `gripping` is the verb, and
`the clipboard edge` is the contact geometry. `clipboard` is REPEATED rather
than pronominalised on purpose: CLIP has no coreference, and the guard has TWO
hands -- a bare `fingers` clause can settle on the pointing hand, which already
has fingers. Naming the object is what binds the digits to the right one.

WHY NOT "hand visible". It is a visibility predicate, not a summoned object, and
visibility is not the failure -- a hand-shaped form IS visible, it is a mitten.
Articulation is the failure, so the words name articulated parts.

THE BUDGET, MEASURED AND NOT ESTIMATED. The parent's prompt runs 64 of 77 on
animagine's own CLIP vocab (pipeline/clip_token_count.py, offline, the model's
own vocab.json/merges.txt). The child measures 73 of 77 -- nine of the thirteen
free tokens spent, four left, and NOT ONE token of the parent removed. This is
asserted below and the derivation refuses if it ever stops being true, because
SDXL drops the TAIL in silence and this prompt's tail is `masterpiece, best
quality, very aesthetic`.

WHAT IS DELIBERATELY NOT TRIED HERE.

  * THE NEGATIVE IS NOT TOUCHED. It carries `extra hands, extra fingers,
    deformed hands` and it is legitimate to wonder whether those suppress hand
    drawing outright. That is a SECOND variable and a second rung; it is also
    the wrong one to take first, because prompt-summons says the positive
    assertion is the stronger lever and this rung is what measures it. If the
    grip does not arrive, dropping the hand terms from the negative is the named
    next wording rung -- before any hint change.
  * NO FIGURE INK IN THE BOARD HINT. Adding a stroke for the gripping hand would
    be the first figure ink ever placed in that hint and the parent's verdict
    ruled it must be argued against the five tracing losses, not slipped in. It
    is what happens only if wording fails.
  * No scale change, no second seed, no guidance window, no mask change, no
    third figure, no colour-cast fix. No pick, no plate_ack, no canon filename,
    no canon.yaml edit.

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
NEW_ID = "ep2-b08-grip-0820"
OUT = "pipeline/jobs/%s.yaml" % NEW_ID

STAGE = r"C:\banyan-farm\b08grip-0820\src"
# The driver's last commit, and every staged file still hashes to the sha the
# preflight pins -- asserted at the bottom of this script rather than trusted.
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
CEILING = 77

# The one edit, expressed as the exact substring it replaces so the derivation
# cannot silently rewrite anything else in the sentence.
OLD_CLAUSE = "clipboard lowered in one hand,"
NEW_CLAUSE = ("clipboard lowered in one hand, fingers and thumb gripping the "
              "clipboard edge,")


def main() -> int:
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    import yaml as _yaml
    parent = _yaml.safe_load(open(os.path.join(root, PARENT), encoding="utf-8"))
    ppay = {os.path.basename(k.replace("\\", "/")): v
            for k, v in parent["payload"].items()}
    old_prompt = ppay["prompt.txt"]
    assert OLD_CLAUSE in old_prompt, "the clause this rung edits is not in the parent"
    new_prompt = old_prompt.replace(OLD_CLAUSE, NEW_CLAUSE)
    assert new_prompt != old_prompt

    # ---- THE BUDGET, MEASURED ON THE MODEL'S OWN VOCAB BEFORE THE SPEC EXISTS.
    clip = clip_token_count.Clip()
    n_old, _ = clip.count(old_prompt)
    n_new, unknown = clip.count(new_prompt)
    assert not unknown, "tokens unknown to animagine's vocab: %s" % unknown
    total_old = n_old + clip_token_count.SPECIALS
    total_new = n_new + clip_token_count.SPECIALS
    assert total_old == 64, "the parent no longer measures 64: %d" % total_old
    assert total_new <= CEILING, (
        "!! %d of %d -- SDXL would drop this prompt's tail in silence, and its "
        "tail is the quality block." % (total_new, CEILING))

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "beat 08 staging lane, 2026-08-20 -- derived by "
                     "pipeline/derive_b08_grip_0820.py, on the wording rung "
                     "its own parent's verdict named as the cheapest lever.",
            "consumer":
                "Beat 08's plate, and this is the LAST clause between the beat "
                "and a complete plate candidate. The parent put the board in "
                "the frame at a strength that leaves the drawing alone and got "
                "the far arm to reach it; what it did not get is a hand ON it. "
                "The cut needs one frame where the clipboard is HELD, because "
                "'a board carried at the end of a sleeve' is not the picture "
                "the beat's line describes and a plate that is close is still "
                "not a plate.",
            "success":
                "One 832x1216 png with its sidecar, published to "
                "C:\\banyan-farm\\courier-box\\farm-out\\ep2-b08-grip-0820 "
                "with a sha256 manifest, and read at 1:1, 3x AND 5x beside its "
                "parent -- 5x because that is the magnification at which the "
                "parent's mitten was found, and a grip judged at 1:1 is a grip "
                "not judged. The preflight must print its four verification "
                "lines, the sidecar must read `controlnet_2_conditioning_"
                "scale: 0.3` and `seed: 20260819`, and its `prompt:` must "
                "contain `fingers and thumb gripping the clipboard edge`.",
            "why":
                "Nine words, one sample, and every outcome is informative. The "
                "mechanism is proven and the recipe is fixed: every weight is "
                "on the card, both hints are byte-identical to two frames "
                "already rendered, and the parent took 30 seconds of GPU end "
                "to end. If the grip arrives, beat 08 has a COMPLETE plate "
                "candidate for the first time and the route stops. If it does "
                "not, wording has been eliminated as the lever for a hand -- "
                "which is worth knowing before anyone argues for putting "
                "figure ink in a hint that has never carried any.",
        },
        overrides={
            "argv:--arm": "grip",
            "argv:--repo-commit": REPO_COMMIT,
            "payload:prompt.txt": new_prompt,
            # A no-op in value and NOT a no-op in provenance: it forces
            # derive_spec to find the --seed site, patch it, and record
            # derivation.seed, so the house seed pin is asserted rather than
            # inherited by silence.
            "seed": SEED,
        },
        # derive_spec appends (parent id -> new id) itself and runs it LAST, so
        # the two more specific pairs get first refusal on the same substring.
        retoken=[("b08scale30-0820", "b08grip-0820"),
                 ("ep2-b08-scale30-0820-scale30", "ep2-b08-grip-0820-grip")],
        by="pipeline/derive_b08_grip_0820.py",
        extra={
            "bar": {
                "b0_the_stack_is_what_it_claims":
                    "VOID-CHECK, carried from the parent UNCHANGED and it must "
                    "stay unchanged, because this rung's whole claim is that "
                    "only the words moved. Preflight prints `twins net "
                    "verified`, `scribble net verified`, the line asserting the "
                    "two nets share size and config and DIFFER in weights, and "
                    "`staged driver, BOTH hints and BOTH references verified`. "
                    "The sidecar must read `controlnet_conditioning_scale: "
                    "1.0`, `controlnet_2_conditioning_scale: 0.3`, "
                    "`control_image_sha256: 562911c8...`, "
                    "`control_2_image_sha256: 38cd39da...`, `seed: 20260819` "
                    "and both capsule masks unchanged. If any of those differs "
                    "from the parent's sidecar this is not a wording "
                    "comparison and the frame is not a result.",
                "b4a_the_grip":
                    "THE ONE CLAUSE THIS RUNG EXISTS FOR, AND IT IS SCORED AT "
                    "5x. The board is already established -- the parent drew it "
                    "at the authored quad, corners (608.6,660.5) (719.5,678.1) "
                    "(697.7,816.2) (586.7,798.6), bbox x 583-723 y 657-820, at "
                    "the authored 9-degree tilt with its top edge below the "
                    "shoulder line y=491 -- and that MUST SURVIVE. What is "
                    "being added: A DRAWN HAND ON THE BOARD. Passes if at 5x "
                    "there are separated digits at the board's edge -- fingers "
                    "reading as fingers, not a rounded terminal form -- with "
                    "the board's edge passing BEHIND or BETWEEN them rather "
                    "than tucking under a mitten. A thumb is wanted and its "
                    "absence alone is not a fail; the fail is no digits. "
                    "Scored BY EYE at 1:1, 3x and 5x against the parent frame "
                    "side by side. NO EDGE METRIC: the parent's verdict "
                    "established that mean gradient in this region reads lower "
                    "WITH the board than without it, so the number is known to "
                    "point the wrong way here.",
                "b4a_ii_still_one_board":
                    "THE RISK THE EDIT ITSELF CREATES, PRE-REGISTERED BECAUSE "
                    "IT IS THE PRICE OF NAMING THE OBJECT TWICE. `clipboard` "
                    "now appears twice in the positive prompt, which is what "
                    "binds the digits to the right hand, and the standing "
                    "counter-risk is a duplicated object. EXACTLY ONE board or "
                    "clipboard in the frame, at the hint's quad. A second board "
                    "anywhere -- in the pointing hand, on the ground, doubled "
                    "at the same place -- FAILS this clause even if the grip "
                    "arrives, and it would mean the next wording must refer to "
                    "the object once and bind by position instead.",
                "b4b_the_grip_is_on_the_RIGHT_hand":
                    "THE OTHER RISK THE EDIT CREATES. The guard has two hands "
                    "and the other one is POINTING. The fingers must arrive on "
                    "the board-side hand; fingers added to the pointing hand, "
                    "or a pointing gesture that turns into a second grip, is a "
                    "FAIL of this clause and a specific, useful finding about "
                    "how the clause binds. The pointing hand's centroid stays "
                    "within ~60 px of the authored wrist (280.5,695.1): "
                    "twinsipa 40.3, boardnet 10.2, the parent 48.5, so this has "
                    "never failed.",
                "b6_drawn_not_traced":
                    "CARRIED AND PRE-REGISTERED TO SURVIVE. Both figures read "
                    "as DRAWN CHARACTERS at ep2-b08-twinsipa-0819's standard, "
                    "which the parent met: a face with pupils and a set jaw, "
                    "hair with strands, folds in BOTH garments, a legible metal "
                    "clasp, a drawn cuff. Words do not usually move this, and "
                    "if it moves on a nine-word change that is itself the "
                    "finding.",
                "b8_the_guard_has_hair":
                    "CARRIED, AND IT IS NOW AN INSTRUMENT RATHER THAN JUST A "
                    "CANON CHECK. canon.yaml `ep2-guard-hair`: guard B has "
                    "light sandy hair and \\bbald\\b is FORBIDDEN. The parent "
                    "established that with the wording held constant this "
                    "attribute tracks conditioning load -- bald at 1.0+0.8, "
                    "sandy at 1.0+0.3. Conditioning does not move on this rung, "
                    "so hair is pre-registered to stay. If the guard goes bald "
                    "on a WORDING change, the instrument reads a second input "
                    "-- prompt crowding -- and that is worth as much as the "
                    "grip.",
                "b7_no_limb_fragmentation":
                    "CARRIED WITH THE PARENT'S HARD-WON ADMISSIBILITY RULE, "
                    "WHICH IS NOW A STANDING REQUIREMENT ON THIS BEAT. G-R at "
                    "six regions, three per figure. EVERY PROBE BOX IS PLACED "
                    "FRESH ON THIS FRAME AND PUBLISHES THREE THINGS: its "
                    "coordinates, its luma, AND ITS MATERIAL (skin / cloth), "
                    "with skin verified as >=97% skin-coloured pixels in the "
                    "window. Boxes from the parent are NOT reused: the parent "
                    "proved they do not transfer -- scored at twinsipa's "
                    "coordinates it read a false FAIL of 41.5 because the "
                    "goblin's wardrobe had changed under the box, and "
                    "luma-matching a box on the wrong material does not rescue "
                    "it (50.6). Within-figure spread <= 25.0; every guard "
                    "region <= 0.0, every goblin region >= +20.0.",
                "b2_the_identities_separate":
                    "Guard face <= 0.0, goblin face >= +20.0, separation >= "
                    "+20.0. twinsipa +42.0, the parent +60.6. Same material-and-"
                    "luma publication rule as B7.",
                "b4c_the_arm_belongs_to_the_guard":
                    "MUST SURVIVE. The pointing arm grows from the guard's "
                    "shoulder and is human-skinned. Nine mechanisms have held "
                    "it. AND THE HALF THE PARENT WON: the far arm still REACHES "
                    "the board. An arm that goes back to vanishing takes the "
                    "grip question with it and the frame is a regression, not a "
                    "result.",
                "b1_the_pair":
                    "TWO figures and only two, both whole. Two is correct under "
                    "figure_count_ruled_from_the_script_0817.",
                "b3_one_ground_plane":
                    "Both stand on the same grass. twinsipa measured 4 px "
                    "between the two lowest skin rows. Read by eye if the "
                    "automated detector is confounded by foreground grass.",
                "b5_no_colossus":
                    "Neither figure towers; twinsipa measured a stature ratio "
                    "near 1.13 against the authored 1.100. BULK is scored under "
                    "B6, not here.",
            },
            "the_words_and_the_budget": {
                "the_only_edit":
                    "`%s` -> `%s`. Nine words inserted; NOT ONE token of the "
                    "parent's prompt removed, because every one of them was in "
                    "the frame that passed and this rung is not entitled to "
                    "guess which ones mattered." % (OLD_CLAUSE, NEW_CLAUSE),
                "measured_not_estimated":
                    "%d of %d tokens, measured by pipeline/clip_token_count.py "
                    "against animagine-xl-3.1's own vocab.json and merges.txt "
                    "-- not counted in words. The parent measures %d of %d. "
                    "Nine of the thirteen free tokens are spent and four "
                    "remain. The derivation ASSERTS both numbers and refuses to "
                    "write the spec if either moves, because SDXL drops the "
                    "TAIL in silence and this prompt's tail is `masterpiece, "
                    "best quality, very aesthetic`."
                    % (total_new, CEILING, total_old, CEILING),
                "why_these_nine_words":
                    "The parent's verdict names three absences in one sentence "
                    "-- `no fingers, no thumb, no grip` -- so the clause "
                    "asserts all three positively: two nouns, the verb, and the "
                    "contact geometry (`the clipboard edge`). PROMPT-SUMMONS: a "
                    "positively placed assertion beats a negative, and this "
                    "frame's negative already carries hand terms while its "
                    "positive asserted no hand at all. `clipboard` is repeated "
                    "rather than pronominalised because CLIP has no "
                    "coreference and the guard has TWO hands -- a bare "
                    "`fingers` clause can settle on the pointing one. Placed "
                    "immediately after the object clause and before the "
                    "pointing clause, so the two arms stay described in "
                    "separate spans.",
                "what_was_rejected":
                    "`hand visible` (the wording the rung was sketched with) is "
                    "a visibility predicate, not a summoned object, and "
                    "visibility is not the failure -- a hand-shaped form IS "
                    "visible in the parent, it is a mitten. Articulation is the "
                    "failure, so the words name articulated parts. `fingers "
                    "curled around the clipboard edge` measured 74 and says "
                    "less; the chosen clause measures 73 and names the thumb "
                    "and the verb as well.",
            },
            "not_done_on_purpose":
                "ONE sample, ONE arm, ONE edit, and the edit is words. THE "
                "NEGATIVE IS NOT TOUCHED -- it carries `extra hands, extra "
                "fingers, deformed hands` and whether those suppress hands "
                "outright is a real question and a SECOND variable; "
                "prompt-summons says the positive assertion is the stronger "
                "lever, so this rung measures that one and the negative is the "
                "named next wording rung if it fails. NO FIGURE INK IN THE "
                "BOARD HINT: that would be the first ever placed there and the "
                "parent ruled it must be argued against the five tracing "
                "losses, not slipped in, and only after wording has been "
                "tried. No scale change (both stay 1.0 and 0.3), no guidance "
                "window, no second seed, no mask change, no reference change, "
                "no third figure, no colour-cast fix. No pick, no plate_ack, no "
                "canon filename, no canon.yaml edit.",
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
                "(1) DIGITS ON THE BOARD, ONE BOARD, ON THE BOARD-SIDE HAND, "
                "AND EVERY CARRIED CLAUSE SURVIVES -> PASS, and beat 08 has a "
                "COMPLETE PLATE CANDIDATE for the first time: every clause the "
                "beat asks for in one frame. The pixels get STAGED for cut "
                "assembly and said so plainly. It is STILL NOT A PICK and NOT a "
                "plate_ack -- choosing between this frame and its predecessors "
                "is taste and belongs to R4.\n"
                "(2) NO DIGITS, EVERYTHING ELSE HELD -> wording is ELIMINATED "
                "as the lever for a hand on this route, cleanly, because "
                "nothing else moved. The next rung is the negative's hand terms "
                "(`extra hands, extra fingers, deformed hands`), and only after "
                "that the board hint carrying a stroke for the gripping hand.\n"
                "(3) DIGITS ARRIVE ON THE POINTING HAND, OR A SECOND BOARD "
                "APPEARS -> the clause bound to the wrong referent. Informative "
                "and cheap to fix: the next wording names the object once and "
                "binds by position (`at his hip`) rather than repeating the "
                "noun.\n"
                "(4) THE GRIP ARRIVES AND SOMETHING CARRIED BREAKS -- hair, "
                "wardrobe, the far arm, an identity -> PROMPT CROWDING IS REAL "
                "ON THIS ROUTE AT 73 OF 77, which is a finding that outlives "
                "beat 08 and immediately constrains every other beat's prompt. "
                "Not a pass; the frame would be traded one clause for another.\n"
                "(5) THE BOARD ITSELF DEGRADES -> the second net's product is "
                "sensitive to prompt content at fixed strength, which "
                "contradicts nothing measured so far but would mean the "
                "0.3 result is less robust than one frame suggested, and the "
                "route re-reads before it spends anything else.",
            "who_ruled_this_rung":
                "ep2-b08-scale30-0820's own verdict, under "
                "`next_rung_named_not_taken`: \"ONE sample: THE HAND ON THE "
                "BOARD, with --scale2 held at 0.3 and the board hint held "
                "byte-identical. The cheapest lever first, because it is free "
                "and because the wording is already half-right... the change is "
                "to make the GRIP explicit and nothing else... it is a WORDING "
                "rung so its risk is the token budget (the prompt currently "
                "runs 64 of 77).\" Route log pipeline/b08-arm-route-0819.md "
                "section 17 says the same in the same words. Fired immediately: "
                "the job has no dependency -- every weight is on the card and "
                "both hints already exist -- so it goes to backlog now rather "
                "than waiting for anyone to be awake. Written in an `extra` key "
                "because `fresh` prose is retokened and a parent id there would "
                "become this job's own id.",
            "why_these_key_names":
                "`scoring_rule_pre_registered` and `rights_and_weights` are "
                "this spec's `verdict_rule` and `licence_note`. derive_spec's "
                "FINDINGS_NAME guard refuses any extra key matching "
                "/verdict|licen[cs]/, which is right for findings and "
                "over-reaches on two house keys that must be written BEFORE the "
                "pixels. Same declaration the last three rungs made.",
        },
    )

    # The render step's NAME is a bare word, not a token retoken can reach.
    step = [s for s in child["steps"] if s["name"] == "scale30"][0]
    step["name"] = "grip"

    # ---- ASSERTIONS. EVERY conditioning input is carried byte-for-byte and the
    # ---- ONLY thing that may differ from the parent is the prompt text.
    argvs = [str(a) for s in child["steps"] for a in s["argv"]]

    def flag(n):
        return [argvs[i + 1] for i, v in enumerate(argvs) if v == n]

    assert flag("--scale") == ["1.0"], flag("--scale")
    assert flag("--scale2") == ["0.3"], flag("--scale2")
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
    assert flag("--arm") == ["grip"], flag("--arm")
    assert flag("--root") == [STAGE], flag("--root")
    assert flag("--repo-commit") == [REPO_COMMIT], flag("--repo-commit")
    assert [s["name"] for s in child["steps"]] == ["preflight", "grip",
                                                   "publish"]

    # the mask capsules did not move a digit, compared as text against the parent
    pargv = [str(a) for s in parent["steps"] for a in s["argv"]]
    pcaps = [pargv[i + 1] for i, v in enumerate(pargv)
             if v == "--ip-mask-capsules"]
    assert flag("--ip-mask-capsules") == pcaps, "the capsule masks moved"

    runnable = "\n".join(argvs + list(child.get("payload") or {})
                         + [str(x) for x in (child.get("artifacts") or [])])
    assert PARENT_ID not in runnable, "the parent id survived a runnable path"

    # ---- THE PAYLOAD: the negative is byte-identical, the prompt differs by
    # ---- exactly the inserted clause and by nothing else.
    cpay = {os.path.basename(k.replace("\\", "/")): v
            for k, v in child["payload"].items()}
    assert set(cpay) == set(ppay), (sorted(cpay), sorted(ppay))
    assert cpay["negative.txt"] == ppay["negative.txt"], "the negative moved"
    assert cpay["prompt.txt"] == new_prompt
    assert cpay["prompt.txt"].replace(NEW_CLAUSE, OLD_CLAUSE) == old_prompt, \
        "the prompt differs from the parent's by more than the inserted clause"
    assert "light sandy hair" in cpay["prompt.txt"]
    assert "bald" not in cpay["prompt.txt"], "canon ep2-guard-hair forbids bald"
    assert "fingers and thumb gripping the clipboard edge" in cpay["prompt.txt"]

    # ---- and every staged file on disk still hashes to what the preflight pins
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
    print("variable  the positive prompt, +9 words (nothing else)")
    print("tokens    %d -> %d of %d (%d free)"
          % (total_old, total_new, CEILING, CEILING - total_new))
    print("steps     %s" % " -> ".join(s["name"] for s in child["steps"]))
    print("stage     %s" % STAGE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
