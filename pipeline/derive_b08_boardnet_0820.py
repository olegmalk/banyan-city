#!/usr/bin/env python3
r"""Derive `ep2-b08-boardnet-0820` FROM `ep2-b08-twinsipa-0819`.

THE ONE VARIABLE: A SECOND CONTROLNET, CARRYING THE BOARD AND NOTHING ELSE.
Same twins net, same openpose hint (byte-identical, sha 562911c8), same two
capsule masks, same two references, same ip-scale, same conditioning scale,
same seed, same words. One thing is added: a scribble net reading a hint that
contains one quad.

WHY THIS RUNG EXISTS
-------------------------------------------------------------------------------
`ep2-b08-twinsipa-0819` passed every pre-registered clause on this beat except
B4a, the lowered clipboard, and B4a was pre-registered to FAIL for a reason no
amount of tuning addresses: COCO-18 has eighteen keypoints and all eighteen are
body parts, so a pose hint cannot express an object. Its verdict named the
remedy and declined to take it:

    ONE sample: THE BOARD, via multi-ControlNet -- the openpose skeleton for the
    figures plus a scribble hint carrying the clipboard rectangle at the guard's
    hip, both nets composed on the same pipeline, with these two capsule masks
    and this reference pair carried unchanged. Its bar is B4a alone, with every
    clause passing here pre-registered to survive; its risk is that a second
    ControlNet re-opens the tracing question the scribble net lost on five
    times, so its hint must carry the BOARD ONLY and no figure contour.

That is this job, and the risk it names is why `author_b08_board_hint.py`
asserts the absence of figures AS PIXELS rather than promising it in a comment.

WHY THE BOARD HINT CAN BE TRUSTED NOT TO RE-OPEN B6
-------------------------------------------------------------------------------
The scribble net's five losses on this beat were all the same loss: a closed
contour around a BODY is an instruction about where that body's edge goes, and
the net obeys it, producing a traced outline instead of a drawn character. What
the net does well with enclosure is exactly what a rectangular board needs --
and `author_b08_pose_hint` has said so all along, in the one place it kept a
rectangle: "it is an object we want traced, not a body we want redrawn, and B4a
has passed on it four times."

So the second hint contains one quad and its clip. `--selftest` asserts every
lit pixel falls inside that quad dilated by the stroke; that ZERO lit pixels
fall anywhere on the goblin; and that the set of guard limbs the ink meets is
EXACTLY {gripping forearm, torso, left thigh} -- the three a clipboard held at
the hip physically occludes. His face and his pointing arm are asserted
untouched by name.

THE BOARD IS PINNED TO THE SKELETON, NOT DESCRIBED TWICE
-------------------------------------------------------------------------------
The board's grip point equals `stage()`'s guard L-wrist TO THE FLOAT --
(621.6704, 668.4352). The openpose hint puts his wrist there precisely so the
arm holding the board goes somewhere sensible, and the board hint now derives
the same point from the same constants. Two files, one board, one assertion
holding them together.

WHAT WAS VERIFIED ON THE BOX BEFORE THIS WAS WRITTEN (read-only, $0)
-------------------------------------------------------------------------------
diffusers 0.29.2, from the installed source and not from memory:
  * `auto_pipeline.py:401` -- `passed_class_obj = {k: kwargs.pop(k) for k in
    expected_modules if k in kwargs}`. No isinstance filter, so a LIST passed as
    `controlnet=` survives `from_pipe` verbatim.
  * `pipeline_controlnet_sd_xl.py:266-267` -- `if isinstance(controlnet, (list,
    tuple)): controlnet = MultiControlNetModel(controlnet)`. The list is wrapped
    in `__init__`.
  * `pipeline_controlnet_sd_xl.py:~1226-1232` -- scalar `control_guidance_start`
    / `_end` are broadcast to `mult = len(controlnet.nets)` entries, so passing
    0.0/1.0 as floats stays correct with two nets.
  * `pipeline_controlnet_sd_xl.py:1488-1495` -- the ControlNet forward receives
    `added_cond_kwargs=controlnet_added_cond_kwargs` and NOT
    `cross_attention_kwargs`. The masked IP-Adapter therefore reaches the UNet
    only; the two nets, which have no adapter loaded, never see
    `ip_adapter_masks`. This was the one composition question that could have
    crashed the job.
  * The scribble net is complete in the box cache: 2502139104 bytes, sha256
    b3e4ac47..., config sha b5b8f9a7..., zero `.incomplete`, and NO fp16 variant
    file -- so `CONTROLNET_VARIANT = None` is right for it too.
  * 24463 MiB card with 24137 MiB free. Two bf16 ControlNets add ~2.3 GiB over
    the parent, which rendered in 18.4s.

THE TRAP THE PREFLIGHT EXISTS FOR, AND IT IS A NEW ONE
-------------------------------------------------------------------------------
The scribble blob and the twins blob are THE SAME SIZE -- 2502139104 bytes each
-- and carry the BYTE-IDENTICAL config.json, sha b5b8f9a7. Same architecture,
different weights. So size, file count and config all pass whichever net is in
whichever directory, and ONLY the weight sha can tell the pose net from the
object net. That is `mac_preflight`'s lesson arriving on a second machine, and
the preflight below asserts the two shas are DIFFERENT rather than merely
checking each in isolation.

$0. Writes one yaml file. No GPU, no network, nothing enqueued.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b08-twinsipa-0819.yaml"
PARENT_ID = "ep2-b08-twinsipa-0819"
NEW_ID = "ep2-b08-boardnet-0820"
OUT = "pipeline/jobs/%s.yaml" % NEW_ID

STAGE = r"C:\banyan-farm\b08boardnet-0820\src"
REPO_COMMIT = "ee74ac0e3eaf920fc7637fa7e4f2727af7684628"

TWINS_DIR = r"C:\banyan-farm\cnet-openpose-twins"
TWINS_SHA = "54a2afb1bd21349e475566e5428884bc937a4caecf863b29dea08acc40612fa4"
SCRIBBLE = "xinsir/controlnet-scribble-sdxl-1.0"
SCRIBBLE_SHA = "b3e4ac47bc814019d50dc842f579301440deb6d8f09ee1b91a30f527ace1b852"
CONFIG_SHA = "b5b8f9a7619c9452f19407ef73a01ce3f061fcf932de43ddbaca336d12d02801"
NET_BYTES = 2502139104

DRIVER_SHA = "aff188907fa03914b30a8cec2e5f739a5c4941f5d4246f4b2e220a9cc047c66a"
POSE_HINT = "pipeline/control/b08-openpose-nat-0819.png"
POSE_SHA = "562911c8174a6ecc21bc8710a1ac1b7f965c3f2d865093a742c2598c37d952e0"
BOARD_HINT = "pipeline/control/b08-board-0820.png"
BOARD_SHA = "38cd39da304dbb0317aa2522e1ccca099bef583e88e6573fde03b287358213d6"
REF_GOBLIN = "pipeline/control/b08-ref-goblin-0819.png"
REF_GOBLIN_SHA = "13b0c69d2f95dad6fd5472d8ab0310967b1a88c4554de7e6ff74b2d3e3644d8c"
REF_GUARD = "pipeline/control/b08-ref-guard-0819.png"
REF_GUARD_SHA = "61dc3f7fbd052617e52db63e8f6d359822b6ceba14b13514ffc03179b56cd83c"

SCALE2 = "0.8"

PREFLIGHT = r'''# GUARD, NOT A VARIABLE. Carried from the parent and EXTENDED to the
# SECOND NET and the SECOND HINT. Every input that conditions this frame is
# re-read here before a GPU second is spent.
#
# THE NEW TRAP, AND IT IS THE REASON THE TWO SHAS ARE COMPARED TO EACH OTHER
# RATHER THAN ONLY TO CONSTANTS: the scribble blob and the twins blob are
# THE SAME SIZE (2502139104 bytes) and ship the BYTE-IDENTICAL config.json.
# Same architecture, different weights. Size, file count and config pass
# whichever net sits in whichever directory, so only the weight sha can tell
# the POSE net from the OBJECT net -- and swapping them would condition the
# skeleton on the board hint and the board on the skeleton.
import glob, hashlib, os, sys

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()

d = r"C:\banyan-farm\cnet-openpose-twins"
blob = os.path.join(d, "diffusion_pytorch_model.safetensors")
n = os.path.getsize(blob)
if n != %(bytes)d:
    print("!! twins blob is %%d bytes, expected %(bytes)d" %% n); sys.exit(1)
got = sha(blob)
if got != "%(twins)s":
    print("!! twins blob sha %%s, expected %(twins)s" %% got); sys.exit(1)
ch = hashlib.sha256(open(os.path.join(d, "config.json"), "rb").read()).hexdigest()
if ch != "%(cfg)s":
    print("!! twins config sha %%s, expected %(cfg)s" %% ch); sys.exit(1)
bad = [r for r, _, fs in os.walk(d) for f in fs if f.endswith(".incomplete")]
if bad:
    print("!! .incomplete under the twins dir: %%r" %% bad); sys.exit(1)
print("twins net verified: %%d bytes, sha %%s" %% (n, got))

# ---- THE SECOND NET, resolved out of the offline HF cache by repo id.
sd = r"C:\Users\artvn\.cache\huggingface\hub\models--xinsir--controlnet-scribble-sdxl-1.0"
snaps = glob.glob(os.path.join(sd, "snapshots", "*"))
if len(snaps) != 1:
    print("!! expected exactly 1 scribble snapshot, found %%r" %% snaps); sys.exit(1)
sblob = os.path.realpath(os.path.join(snaps[0], "diffusion_pytorch_model.safetensors"))
sn = os.path.getsize(sblob)
if sn != %(bytes)d:
    print("!! scribble blob is %%d bytes, expected %(bytes)d" %% sn); sys.exit(1)
sgot = sha(sblob)
if sgot != "%(scrib)s":
    print("!! scribble blob sha %%s, expected %(scrib)s" %% sgot); sys.exit(1)
sch = hashlib.sha256(open(os.path.join(snaps[0], "config.json"), "rb").read()).hexdigest()
if sch != "%(cfg)s":
    print("!! scribble config sha %%s, expected %(cfg)s" %% sch); sys.exit(1)
sbad = [r for r, _, fs in os.walk(sd) for f in fs if f.endswith(".incomplete")]
if sbad:
    print("!! .incomplete under the scribble dir: %%r" %% sbad); sys.exit(1)
if glob.glob(os.path.join(snaps[0], "*fp16*")):
    print("!! a fp16 variant appeared; the driver passes variant=None"); sys.exit(1)
print("scribble net verified: %%d bytes, sha %%s" %% (sn, sgot))

# ---- AND THE TWO ARE NOT THE SAME WEIGHTS, asserted rather than assumed.
if got == sgot:
    print("!! THE TWO NETS ARE THE SAME WEIGHTS. One of the two directories "
          "holds a copy of the other and this render would condition the "
          "skeleton and the board on one net."); sys.exit(1)
if n != sn or ch != sch:
    print("!! the two nets no longer share size and config, so the premise of "
          "this guard has changed and it must be re-read, not relaxed."); sys.exit(1)
print("the two nets share size %%d and config %%s and DIFFER in weights -- "
      "only the sha separates them" %% (n, ch))

for rel, want in (("pipeline/controlnet_plate.py", "%(driver)s"),
                  ("%(pose)s", "%(pose_sha)s"),
                  ("%(board)s", "%(board_sha)s"),
                  ("%(refg)s", "%(refg_sha)s"),
                  ("%(refu)s", "%(refu_sha)s")):
    p = os.path.join(r"%(stage)s", rel.replace("/", os.sep))
    if not os.path.exists(p):
        print("!! staged file missing: %%s" %% p); sys.exit(1)
    hh = sha(p)
    if hh != want:
        print("!! %%s sha %%s, expected %%s" %% (p, hh, want)); sys.exit(1)
print("staged driver, BOTH hints and BOTH references verified")''' % {
    "bytes": NET_BYTES, "twins": TWINS_SHA, "scrib": SCRIBBLE_SHA,
    "cfg": CONFIG_SHA, "driver": DRIVER_SHA, "pose": POSE_HINT,
    "pose_sha": POSE_SHA, "board": BOARD_HINT, "board_sha": BOARD_SHA,
    "refg": REF_GOBLIN, "refg_sha": REF_GOBLIN_SHA,
    "refu": REF_GUARD, "refu_sha": REF_GUARD_SHA, "stage": STAGE,
}


def main() -> int:
    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "beat 08 staging lane, 2026-08-20 -- derived by "
                     "pipeline/derive_b08_boardnet_0820.py under the judge "
                     "lane's naming of this rung.",
            "consumer":
                "Beat 08's plate, for its cut slot in the episode 2 assembly. "
                "The parent is the first frame on this beat that could "
                "plausibly BE that plate: staging, gesture and per-limb "
                "identity all landed in one render. Exactly one "
                "pre-registered clause is still failing, B4a, and it is the "
                "beat's own done_when -- \"the clipboard comes DOWN\". "
                "Whoever assembles the cut needs to know whether a second "
                "ControlNet closes that clause without spending any of the "
                "nine the parent bought, because a plate with no clipboard "
                "does not satisfy the beat and a plate whose figures got "
                "traced is worse than the one we already have.",
            "success":
                "One 832x1216 png with its sidecar, published to "
                "C:\\banyan-farm\\courier-box\\farm-out\\ep2-b08-boardnet-0820 "
                "with a sha256 manifest, and read at 1:1 and at 3x beside the "
                "PARENT's frame -- which is the control for this rung, being "
                "the same seed, same prompt and same everything but the second "
                "net. The preflight must print `twins net verified`, `scribble "
                "net verified` and `staged driver, BOTH hints and BOTH "
                "references verified`, and the sidecar must name "
                "controlnet_2, its scale and control_2_image_sha256; without "
                "all of that the job has no result and the render is not "
                "scored.",
            "why":
                "The board cannot be reached from where the parent stands: "
                "COCO-18's eighteen keypoints are all body parts, so no "
                "conditioning scale on the pose net will ever put an object in "
                "a hand. A second net is the only mechanism, the composition "
                "was verified read-only against the installed diffusers "
                "0.29.2 source before this spec was written, both nets are "
                "already on the card, and the board hint's own selftest proves "
                "it carries no figure pixel. Two minutes, $0, no download, no "
                "provider.",
        },
        overrides={
            "argv:--arm": "boardnet",
            "argv:--repo-commit": REPO_COMMIT,
        },
        retoken=[("b08twinsipa-0819", "b08boardnet-0820"),
                 ("ep2-b08-twinsipa-0819-twinsipa",
                  "ep2-b08-boardnet-0820-boardnet"),
                 (PARENT_ID, NEW_ID)],
        by="pipeline/derive_b08_boardnet_0820.py",
        extra={
            "bar": {
                "b0_the_stack_is_what_it_claims":
                    "VOID-CHECK, READ FIRST, FOUR LINES, and it grew a line "
                    "because it grew a net. (i) preflight prints `twins net "
                    "verified: %d bytes, sha 54a2afb1...`; (ii) preflight "
                    "prints `scribble net verified: %d bytes, sha "
                    "b3e4ac47...`; (iii) preflight prints that the two nets "
                    "SHARE size and config and DIFFER in weights -- the two "
                    "blobs are byte-for-byte the same length and ship the same "
                    "config.json, so a size check cannot tell the pose net "
                    "from the object net and only the sha can; (iv) the "
                    "sidecar reads `controlnet_2: %s`, "
                    "`controlnet_2_conditioning_scale: %s`, "
                    "`control_2_image_sha256: %s`, AND still reads "
                    "`ip_adapter_mask_geometry: capsules` with "
                    "`ip_adapter_masks_overlap: false`. Missing any of the "
                    "four and the frame is VOID -- \"the second net did "
                    "nothing\" and \"the second net never loaded\" are "
                    "different findings and this rung must not confuse them."
                    % (NET_BYTES, NET_BYTES, SCRIBBLE, SCALE2, BOARD_SHA),
                "b4a_board_down":
                    "THIS RUNG'S OWN QUESTION, AND IT IS THE BEAT'S OWN "
                    "done_when, quoted verbatim from "
                    "review/ep2-picks/done-definitions.yaml beat 08: \"the "
                    "clipboard comes DOWN and the point goes to the BELLY, "
                    "both legible\".\n\n"
                    "INSTRUMENT, AND THE PARENT IS THE CONTROL. Same seed, "
                    "same prompt, same pose hint, same masks, same references "
                    "-- the ONLY difference between the two frames is the "
                    "second net, so the two frames are read side by side and "
                    "the authored board region is compared between them. The "
                    "authored quad's corners are (608.6,660.5) (719.5,678.1) "
                    "(697.7,816.2) (586.7,798.6); its bounding box is "
                    "x 583-723, y 657-820.\n\n"
                    "PASSES IF, read at 1:1 and at 3x, a flat rectangular "
                    "board or clipboard is legibly drawn, held at or near the "
                    "guard's lowered far hand, with its top edge BELOW his "
                    "shoulder line (y=491). The verdict publishes: whether the "
                    "object is present, where its corners actually landed "
                    "against the four authored ones, and the same reading "
                    "taken on the PARENT frame in the same box -- which has no "
                    "board and is the negative control. `Legible` is the "
                    "beat's word and it is scored by eye at 3x; the corner "
                    "geometry is the number that says whether the second net "
                    "put it WHERE it was asked.",
                "b6_drawn_not_traced":
                    "CARRIED, AND ON THIS RUNG IT IS LOAD-BEARING RATHER THAN "
                    "ROUTINE -- it is the clause a second net most endangers. "
                    "The scribble net lost the figure-tracing question five "
                    "times on this beat, and the parent's verdict named that "
                    "as this rung's risk. Both figures must still read as "
                    "DRAWN CHARACTERS and must NOT get worse than the parent, "
                    "which improved markedly on its own parent: a face with "
                    "pupils and a set jaw, hair with strands, folds in both "
                    "garments, a legible metal clasp. A frame that delivers "
                    "the board and returns traced outlines FAILS this clause "
                    "and the rung does not pass -- the board is not worth the "
                    "drawing.",
                "b7_no_limb_fragmentation":
                    "CARRIED UNCHANGED FROM THE PARENT, WITH THE PARENT'S OWN "
                    "INSTRUMENT WARNING PROMOTED INTO THE BAR.\n\n"
                    "G-R sampled at SIX regions, three per figure -- face, "
                    "forearm, shin -- each box placed ON THE DRAWN LIMB at 1:1 "
                    "and its coordinates published. PASSES IF each figure's "
                    "WITHIN-FIGURE SPREAD (max minus min across its three "
                    "regions) is <= 25.0 levels, AND every guard region is "
                    "<= 0.0 with every goblin region >= +20.0.\n\n"
                    "THE PROBES MUST BE LUMA-MATCHED AND MUST PUBLISH THEIR "
                    "LUMA. This is not advice, it is a condition of the "
                    "measurement being admissible. The parent established that "
                    "G-R COMPRESSES WITH LUMA: sweeping the goblin's leg in "
                    "30px bands, G-R fell 28.3 -> 13.7 from y920 to y1130 "
                    "while luma fell 196.9 -> 105.1, so a probe drifting into "
                    "grass shadow invents fragmentation that is not there. The "
                    "parent's six final probes sat at luma 196.9-250.1. Any "
                    "probe here that cannot be placed at comparable luma is "
                    "reported UNMEASURABLE, not scored.",
                "b2_the_identities_separate":
                    "CARRIED. Guard face <= 0.0, goblin face >= +20.0, "
                    "separation >= +20.0. The parent measured +42.0. Scored to "
                    "catch the second net dragging the two identities around, "
                    "not because it is in doubt.",
                "b4b_both_arms_stay_on_their_skeletons":
                    "MUST SURVIVE. The guard's hand centroid within ~60 px of "
                    "the authored wrist (280.5,695.1) -- the parent measured "
                    "40.3 px. The goblin's arms hang, hands near y~900, and "
                    "the two hands must not clasp. NOTE THE SPECIFIC HAZARD "
                    "THIS RUNG ADDS: the board hint's ink legitimately meets "
                    "the guard's GRIPPING forearm, and if the second net "
                    "pulls his POINTING arm toward the board instead, that "
                    "shows up here first.",
                "b4c_the_arm_belongs_to_the_guard":
                    "MUST SURVIVE, seventh mechanism. The pointing arm grows "
                    "from THE GUARD's shoulder and its skin matches its owner "
                    "(the parent read -3.3 on that forearm).",
                "b8_the_guard_has_hair":
                    "PRE-REGISTERED BECAUSE AN UNASSERTED ATTRIBUTE FALLS TO "
                    "WORDING, AND HERE THE WORDING IS THE ONLY CANON-CORRECT "
                    "PART OF THE STACK. canon.yaml `ep2-guard-hair`: \"The "
                    "approved guards have HAIR. Guard A dark cropped hair, "
                    "guard B light sandy hair\", and it FORBIDS \\bbald\\b. "
                    "Beat 08's actor is Guard 2 = guard B = light sandy hair. "
                    "THE IP-ADAPTER REFERENCE IS BALD BY CONSTRUCTION -- "
                    "author_b08_ip_refs.GUARD_BOX is commented \"bald human "
                    "head, brown cloak, cream collar\", cut from "
                    "ep2-b08-boardcomp-0818, a plate that predates the hair "
                    "ruling. The prompt says `light sandy hair` and the parent "
                    "came back sandy-haired, so on this route the wording beat "
                    "the reference and the frame is canon-correct while its "
                    "own reference is not. PASSES IF the guard has hair and is "
                    "not bald. A regression to bald here means the second net "
                    "shifted the balance toward the reference, which would be "
                    "a real finding about multi-net composition and not a "
                    "cosmetic miss.",
                "b1_the_pair":
                    "TWO figures and only two, both whole in frame. Two is "
                    "CORRECT and not a shortfall: "
                    "`figure_count_ruled_from_the_script_0817` ruled the "
                    "done_when's \"both guards and the scavenger\" clause "
                    "refutes itself -- the script's stage direction names one "
                    "guard as the actor and the scavenger's belly as the "
                    "target -- and REMOVED the three-figure blocker on this "
                    "beat.",
                "b3_one_ground_plane":
                    "Both stand on the same grass. The parent measured 4 px "
                    "between the two lowest skin rows; the ankles are not "
                    "touched by this rung.",
                "b5_no_colossus":
                    "Neither figure towers. The parent measured a stature "
                    "ratio near 1.13 against the authored 1.100.",
            },
            "not_done_on_purpose":
                "ONE sample, ONE arm, ONE variable. The second net's scale is "
                "0.8 because that is the ONLY conditioning scale this repo has "
                "measured for the scribble net and the value the four passing "
                "B4a frames used -- it is not a tuned number and it is not "
                "swept here. No ip-scale sweep, no second seed, no re-authored "
                "openpose hint (it is byte-identical, sha 562911c8), no change "
                "to either capsule mask, no change to the references, no third "
                "figure, no prompt change of any kind, no purple-cast fix, no "
                "pick, no plate_ack waiver, no canon filename, and no edit to "
                "canon.yaml. The purple cast the parent returned is expected "
                "to persist and is not addressed.",
            "the_hint_carries_no_figure":
                "THE ONE THING A READER SHOULD CHECK FIRST, because it is the "
                "single way this rung can spend what the parent bought. The "
                "second hint is drawn by pipeline/author_b08_board_hint.py and "
                "contains ONE closed quad plus its clip. Its --selftest "
                "asserts, as pixels and not as prose: every lit pixel falls "
                "inside the quad dilated by the stroke; ZERO lit pixels fall "
                "anywhere on the goblin's capsule mask; and the set of guard "
                "limbs the ink meets is EXACTLY {gripping forearm, torso, left "
                "thigh}, the three a clipboard held at the hip occludes, with "
                "his face and his pointing arm asserted untouched BY NAME. The "
                "board's grip point equals the openpose skeleton's guard "
                "L-wrist TO THE FLOAT, (621.6704, 668.4352), so the object and "
                "the hand that holds it cannot drift apart across two files. "
                "Ink fraction 0.00324.",
            "an_inherited_defect_reported_not_fixed":
                "The clip line across the board's top edge is COLLINEAR with "
                "that edge in BOTH hint authors, so it adds no distinct mark "
                "and cannot be, as author_b08_pose_hint's comment claims, "
                "\"what makes a rectangle read as a clipboard\". Measured at "
                "0.00 px off the edge. It is reproduced UNCHANGED because this "
                "geometry is what B4a passed on four times and this rung's one "
                "variable is the second net. Offsetting the clip so it "
                "actually reads is a candidate for a later rung, on its own.",
            "rights_and_weights":
                "THIS IS THE `licence_note`. Clean, and now TWO nets carry "
                "terms. Base cagliostrolab/animagine-xl-3.1 (CreativeML Open "
                "RAIL++-M). Net 1: xinsir/controlnet-openpose-sdxl-1.0 twins "
                "variant, apache-2.0, allowlisted in the driver by its "
                "upstream repo, blob name and digest. Net 2: "
                "xinsir/controlnet-scribble-sdxl-1.0, apache-2.0, no "
                "attribution condition, the driver's default net and its "
                "original allowlist entry. IP-Adapter h94/IP-Adapter, "
                "apache-2.0. Both references are repo-internal crops. BOTH "
                "hints are authored in PIL from numbers -- no annotator, so "
                "the lllyasviel/Annotators landmine is untouched by either "
                "condition. MistoLine was NOT used and its standing "
                "visible-attribution obligation is not attached to this frame.",
            "scoring_rule_pre_registered":
                "THIS IS THE `verdict_rule`, WRITTEN BEFORE THE PIXELS, and "
                "all five branches close something.\n"
                "(1) BOARD ARRIVES AND EVERY CARRIED CLAUSE SURVIVES -> PASS, "
                "and BEAT 08 HAS A COMPLETE PLATE CANDIDATE: every "
                "pre-registered clause on the beat met in one frame. The "
                "pixels get staged where the next cut assembly can reach them "
                "and the fact is stated plainly. It is still NOT a pick and "
                "NOT a plate_ack -- choosing the plate is a taste call (R4).\n"
                "(2) BOARD ARRIVES BUT B6 DEGRADES (either figure traced) -> "
                "the second net bought the object and spent the drawing. The "
                "next rung is ONE sample at a lower --scale2, and B6's "
                "severity names how much lower.\n"
                "(3) NO BOARD AT ALL, and the authored region is EMPTY -> a "
                "hint this sparse does not reach the scribble net at 0.8. Next "
                "rung raises --scale2 or thickens the stroke; which one is "
                "named by whether ANY structure appeared in the region.\n"
                "(4) SOMETHING APPEARS IN THE AUTHORED REGION BUT IS NOT A "
                "BOARD (a smear, a fence, a second figure) -> the net read the "
                "quad as scenery rather than as a held object. That is a "
                "WORDING question next, not a scale one: the prompt already "
                "says `clipboard lowered in one hand` and the negative already "
                "says `raised clipboard, second board`.\n"
                "(5) A BOARD APPEARS SOMEWHERE ELSE, or two boards appear -> "
                "the second condition is mis-registered. Read "
                "`control_2_image_sha256` in the sidecar FIRST: that tells a "
                "resized or wrong hint (a driver bug, not a result) from the "
                "net genuinely relocating the object.",
            "who_ruled_this_rung":
                "ep2-b08-twinsipa-0819's verdict, under "
                "`next_rung_named_not_taken`, named this rung in full -- "
                "multi-ControlNet, the openpose skeleton unchanged plus a "
                "scribble hint carrying the clipboard only, these two capsule "
                "masks and this reference pair carried unchanged -- and "
                "identified its risk as the tracing question. The driver "
                "gained --controlnet2 at commit ee74ac0e for it. Written in an "
                "`extra` key because `fresh` prose is retokened and a parent "
                "id there would become this job's own id.",
            "why_these_key_names":
                "`scoring_rule_pre_registered` and `rights_and_weights` are "
                "this spec's `verdict_rule` and `licence_note`. derive_spec's "
                "FINDINGS_NAME guard refuses any extra key matching "
                "/verdict|licen[cs]/, which is right for findings and "
                "over-reaches on two house keys that must be written BEFORE "
                "the pixels. Renamed rather than worked around, and declared "
                "here -- the same declaration the parent made.",
        },
    )

    # ---- THE SECOND NET, THE SECOND HINT, AND THE STEP TEXT ---------------
    # Inserted positionally before --prompt-file, the same way the parent
    # inserted its references: the driver takes them as ordinary flags, and the
    # assertions below pin every one of them rather than trusting the splice.
    step = [s for s in child["steps"] if s["name"] == "boardnet"][0] \
        if any(s["name"] == "boardnet" for s in child["steps"]) \
        else [s for s in child["steps"] if s["name"] == "twinsipa"][0]
    step["name"] = "boardnet"
    i = step["argv"].index("--prompt-file")
    step["argv"][i:i] = [
        "--controlnet2", SCRIBBLE,
        "--control2", BOARD_HINT,
        "--control2-sha256", BOARD_SHA,
        "--scale2", SCALE2,
    ]

    child["steps"][0]["argv"][2] = PREFLIGHT

    # ---- publish the SECOND hint too. A frame conditioned on two images whose
    # ---- second image never left the box is a frame nobody can re-read.
    pub = [s for s in child["steps"] if s["name"] == "publish"][0]
    pub["argv"][2] = pub["argv"][2].replace(
        'glob.glob(ctl_dir + "/b08-openpose-nat-0819.png")',
        'glob.glob(ctl_dir + "/b08-openpose-nat-0819.png")\n'
        '               + glob.glob(ctl_dir + "/b08-board-0820.png")')
    pub["argv"][2] = pub["argv"][2].replace("len(files) >= 7", "len(files) >= 8")

    # ---- two nets need more of the card than one did, and the tag should say so
    child["needs"] = [n for n in child["needs"] if n != "vram12"]
    if "vram20" not in child["needs"]:
        child["needs"].insert(1, "vram20")
    child["est_minutes"] = 8

    # ---- ASSERTIONS. Every one is a way a "one variable" rung silently
    # ---- becomes a two-variable one.
    argvs = [str(a) for s in child["steps"] for a in s["argv"]]
    # THE RUNNABLE SURFACE ONLY. The parent id MUST still appear in prose --
    # `who_ruled_this_rung` cites it on purpose, and that is the whole reason
    # that key is an `extra` rather than `fresh` (fresh prose is retokened, and
    # a parent id there would silently become this job's own id). What must not
    # survive is a parent id in anything a RUNNER reads: an argv token, a
    # payload path, an output path. That is what is checked.
    runnable = "\n".join(argvs
                         + list(child.get("payload") or {})
                         + [str(x) for x in (child.get("artifacts") or [])])

    def flag(n):
        return [argvs[i + 1] for i, v in enumerate(argvs) if v == n]

    # the parent's conditioning, carried BYTE-FOR-BYTE
    assert flag("--control") == [POSE_HINT], flag("--control")
    assert flag("--control-sha256") == [POSE_SHA]
    assert flag("--scale") == ["1.0"], flag("--scale")
    assert flag("--seed") == ["20260819"], flag("--seed")
    assert flag("--controlnet") == [TWINS_DIR]
    assert flag("--ip-ref") == [REF_GOBLIN, REF_GUARD]
    assert flag("--ip-ref-sha256") == [REF_GOBLIN_SHA, REF_GUARD_SHA]
    assert flag("--ip-scale") == ["0.7"], flag("--ip-scale")
    assert len(flag("--ip-mask-capsules")) == 2
    assert "--ip-mask" not in argvs, "a rect mask leaked into a capsule job"
    # the one variable
    assert flag("--controlnet2") == [SCRIBBLE], flag("--controlnet2")
    assert flag("--control2") == [BOARD_HINT], flag("--control2")
    assert flag("--control2-sha256") == [BOARD_SHA]
    assert flag("--scale2") == [SCALE2], flag("--scale2")
    assert flag("--arm") == ["boardnet"], flag("--arm")
    assert flag("--repo-commit") == [REPO_COMMIT]
    assert flag("--root") == [STAGE], flag("--root")
    assert PARENT_ID not in runnable, \
        "the parent id survived into a runnable path: %s" % runnable
    assert [s["name"] for s in child["steps"]] == ["preflight", "boardnet",
                                                   "publish"]
    # the preflight names both nets and refuses their confusion
    pf = child["steps"][0]["argv"][2]
    for needle in (TWINS_SHA, SCRIBBLE_SHA, CONFIG_SHA, DRIVER_SHA, BOARD_SHA,
                   POSE_SHA, "THE TWO NETS ARE THE SAME WEIGHTS",
                   "scribble net verified",
                   "staged driver, BOTH hints and BOTH references verified"):
        assert needle in pf, "preflight lost %r" % needle
    # the words did not move
    import yaml as _yaml
    parent = _yaml.safe_load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", PARENT),
        encoding="utf-8"))
    pp = {os.path.basename(k.replace("\\", "/")): v
          for k, v in parent["payload"].items()}
    cp = {os.path.basename(k.replace("\\", "/")): v
          for k, v in child["payload"].items()}
    assert pp == cp, "payload text drifted from the parent's"
    assert "light sandy hair" in cp["prompt.txt"], \
        "the prompt lost the canon hair assertion"
    assert "bald" not in cp["prompt.txt"], "canon ep2-guard-hair forbids bald"

    # AND THE BOARD HINT ON DISK IS THE ONE THIS SPEC PINS, checked here on the
    # exact string that will be in the argv rather than trusted from a selftest.
    import hashlib
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    for rel, want in ((BOARD_HINT, BOARD_SHA), (POSE_HINT, POSE_SHA),
                      ("pipeline/controlnet_plate.py", DRIVER_SHA)):
        with open(os.path.join(root, rel), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        assert got == want, "%s is %s, spec pins %s" % (rel, got, want)

    out = derive_spec.write(child, OUT)
    print("wrote %s" % out)
    print("id        %s" % child["id"])
    print("parent    %s" % PARENT_ID)
    print("variable  a SECOND ControlNet (%s @ %s) on a board-only hint"
          % (SCRIBBLE, SCALE2))
    print("steps     %s" % " -> ".join(s["name"] for s in child["steps"]))
    print("needs     %s" % ", ".join(child["needs"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
