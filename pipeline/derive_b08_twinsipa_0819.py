#!/usr/bin/env python3
r"""Derive `ep2-b08-twinsipa-0819` FROM `ep2-b08-twins-sample-0819`.

THE ONE VARIABLE: PER-FIGURE IDENTITY, ADDED TO THE STAGING THAT NOW WORKS.
Same twins net, same hint, same conditioning scale, same seed, same words --
plus two masked references. Both mechanisms are individually proven ON THIS
BEAT: masked IP-Adapter moved B2 by 48.5 levels on the contour route
(ep2-b08-ipamask-0819) and twins moved B4b here. Nothing else moves.

WHY IT COULD NOT BE FILED UNTIL NOW, AND WHAT CHANGED
-------------------------------------------------------------------------------
The parent's verdict named this rung and refused to file it, because the masks
that carry identity were RECTANGLES and beat 08's two figures INTERLEAVE: the
guard's pointing hand reaches into the goblin's x-range, so widening her rect
puts her fingertip inside HIS mask and narrowing his puts his own hanging arm
inside HERS. A sample with knowingly-wrong masks is a guess with a GPU attached.

The driver now takes CAPSULE masks -- the union of one dilated segment per limb,
emitted by `author_b08_openpose_hint.figure_capsules` from the SAME keypoints the
hint is drawn from, so a mask cannot disagree with the geometry the ControlNet is
conditioned on. On the real skeletons the two figures' masks share NO lit pixel
while their BOUNDING BOXES DO overlap, which is precisely the case rectangles
cannot express. Measured clearance: disjoint through r=13, colliding at r=14, so
R_ARM=12 is a measured value and not a chosen one.

WHAT THIS RUNG IS FOR
-------------------------------------------------------------------------------
The parent came back with the guard's forearms GREEN and the goblin's legs PALE.
Identity stopped broadcasting BETWEEN the figures and started fragmenting WITHIN
them, and the beat's standing head-only instrument reported its best number ever
(+121.4) on that frame -- so the instrument is now a known trap and this spec
samples PER REGION instead.

$0. Writes one yaml file. No GPU, no network, nothing enqueued.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402
import author_b08_openpose_hint as hint  # noqa: E402

SRC = "pipeline/jobs/ep2-b08-twins-sample-0819.yaml"
PARENT_ID = "ep2-b08-twins-sample-0819"
NEW_ID = "ep2-b08-twinsipa-0819"
OUT = "pipeline/jobs/%s.yaml" % NEW_ID

STAGE = r"C:\banyan-farm\b08twinsipa-0819\src"
DRIVER = "pipeline/controlnet_plate.py"
DRIVER_SHA = "33c438163ce1314ff989f337e9472f08dcbabd5815cb096527e20e13631b7f7a"
REPO_COMMIT = "89860969c2086526d9505a6a2eceeb1f769a29f7"

HINT = "pipeline/control/b08-openpose-nat-0819.png"
HINT_SHA = "562911c8174a6ecc21bc8710a1ac1b7f965c3f2d865093a742c2598c37d952e0"
TWINS_DIR = r"C:\banyan-farm\cnet-openpose-twins"
TWINS_SHA = "54a2afb1bd21349e475566e5428884bc937a4caecf863b29dea08acc40612fa4"
TWINS_BYTES = 2502139104
CONFIG_SHA = "b5b8f9a7619c9452f19407ef73a01ce3f061fcf932de43ddbaca336d12d02801"

REF_GOBLIN = "pipeline/control/b08-ref-goblin-0819.png"
REF_GOBLIN_SHA = "13b0c69d2f95dad6fd5472d8ab0310967b1a88c4554de7e6ff74b2d3e3644d8c"
REF_GUARD = "pipeline/control/b08-ref-guard-0819.png"
REF_GUARD_SHA = "61dc3f7fbd052617e52db63e8f6d359822b6ceba14b13514ffc03179b56cd83c"
IP_SCALE = "0.7"          # what worked first try on the contour; not swept here

# THE MASKS, GENERATED HERE FROM stage() RATHER THAN TYPED. If the staging ever
# moves, re-running this script moves the masks with it, and the hint's own
# --selftest asserts the two figures stay disjoint.
_g, _go, _meta = hint.stage()
CAPS_GOBLIN = hint.capsule_arg(hint.figure_capsules(_go))
CAPS_GUARD = hint.capsule_arg(hint.figure_capsules(_g))

PREFLIGHT = r'''
# GUARD, NOT A VARIABLE. Carried from the parent and EXTENDED to the two
# references: --controlnet points at a local directory, so the sidecar can only
# record a path, and every input that conditions this frame is re-read here
# before a GPU second is spent.
import hashlib, os, sys
d = r"{tw}"
blob = os.path.join(d, "diffusion_pytorch_model.safetensors")
n = os.path.getsize(blob)
if n != {nb}:
    print("!! twins blob is %d bytes, expected {nb}" % n); sys.exit(1)
h = hashlib.sha256()
with open(blob, "rb") as fh:
    for chunk in iter(lambda: fh.read(1 << 22), b""):
        h.update(chunk)
got = h.hexdigest()
if got != "{ts}":
    print("!! twins blob sha %s, expected {ts}" % got); sys.exit(1)
ch = hashlib.sha256(open(os.path.join(d, "config.json"), "rb").read()).hexdigest()
if ch != "{cs}":
    print("!! twins config sha %s, expected {cs}" % ch); sys.exit(1)
bad = [r for r, _, fs in os.walk(d) for f in fs if f.endswith(".incomplete")]
if bad:
    print("!! .incomplete under the twins dir: %r" % bad); sys.exit(1)
for rel, want in (("{drv}", "{dsha}"), ("{hnt}", "{hsha}"),
                  ("{rgo}", "{rgosha}"), ("{rgu}", "{rgusha}")):
    p = os.path.join(r"{stg}", rel.replace("/", os.sep))
    if not os.path.exists(p):
        print("!! staged file missing: %s" % p); sys.exit(1)
    hh = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if hh != want:
        print("!! %s sha %s, expected %s" % (p, hh, want)); sys.exit(1)
print("twins net verified: %d bytes, sha %s" % (n, got))
print("staged driver, hint and BOTH references verified")
'''.format(tw=TWINS_DIR, nb=TWINS_BYTES, ts=TWINS_SHA, cs=CONFIG_SHA,
           drv=DRIVER, dsha=DRIVER_SHA, hnt=HINT, hsha=HINT_SHA,
           rgo=REF_GOBLIN, rgosha=REF_GOBLIN_SHA,
           rgu=REF_GUARD, rgusha=REF_GUARD_SHA, stg=STAGE).strip()


def main() -> int:
    parent = derive_spec.load(os.path.join(derive_spec.REPO, SRC))

    child = derive_spec.derive(
        src=SRC, new_id=NEW_ID, by="pipeline/derive_b08_twinsipa_0819.py",
        retoken=[
            ("ep2-b08-twins-sample-0819-twins", "ep2-b08-twinsipa-0819-twinsipa"),
            ("b08twins-0819", "b08twinsipa-0819"),
            ("ep2-b08-twins-sample-0819", "ep2-b08-twinsipa-0819"),
        ],
        overrides={
            "argv:--arm": "twinsipa",
            "argv:--repo-commit": REPO_COMMIT,
        },
        fresh={
            # Nothing here names the parent: `fresh` is applied BEFORE the
            # retokeniser, so a parent id written here would be rewritten into
            # this job's own id and the spec would cite itself.
            "owner": ("beat 08 staging lane, 2026-08-20 -- derived by "
                      "pipeline/derive_b08_twinsipa_0819.py, and licensed by the "
                      "steward ruling that approved non-rectangular masks."),
            "consumer": (
                "Beat 08's plate, for its cut slot in the episode 2 assembly, and "
                "this is the first rung that could plausibly BE that plate rather "
                "than answer a question about it. Staging is solved -- two whole "
                "figures, one ground plane, no colossus, the arm on the guard in "
                "five mechanisms, and a hand that now arrives 52.5 px from its "
                "authored wrist. Identity is the last blocker, and it has changed "
                "shape: it no longer smears one attribute across both figures, it "
                "fragments WITHIN each of them. Whoever takes the board rung next "
                "needs to know whether a per-figure image condition fixes that, "
                "because a plate with a green-armed guard cannot be cut."),
            "success": (
                "One 832x1216 png with its sidecar, published to "
                "C:\\banyan-farm\\courier-box\\farm-out\\ep2-b08-twinsipa-0819 with "
                "a sha256 manifest, and read at 1:1 beside the parent's frame with "
                "the six per-region probes measured. The preflight step must print "
                "`twins net verified` and `staged driver, hint and BOTH references "
                "verified`, and the sidecar must read "
                "`ip_adapter_mask_geometry: capsules` with "
                "`ip_adapter_masks_overlap: false`; without all three the job has "
                "no result and the render is not scored."),
            "why": (
                "Both mechanisms are individually proven on this beat and the one "
                "thing that blocked composing them -- rectangular masks cannot "
                "separate two figures whose limbs interleave -- was fixed in the "
                "driver today with the interleaving case as its selftest. Two "
                "minutes, $0, no download, no provider: every weight is on the "
                "card and the references are already in the repo."),
        },
        extra={
            "who_ruled_this_rung": (
                "ep2-b08-twins-sample-0819's verdict named it and deliberately did "
                "not file it, recording the rectangle problem under "
                "`the_mask_geometry_problem_that_rung_must_solve_first` and reading "
                "option (b), non-rectangular masks, as the honest fix. The steward "
                "approved (b) and ordered ONE sample after it. Its sibling "
                "ep2-b08-ipamask-0819 is where the masked IP-Adapter was proven. "
                "Written in an `extra` key because `fresh` prose is retokened and "
                "a parent id there would become this job's own id."),
            "why_these_key_names": (
                "`scoring_rule_pre_registered` and `rights_and_weights` are this "
                "spec's `verdict_rule` and `licence_note`. derive_spec's "
                "FINDINGS_NAME guard refuses any extra key matching "
                "/verdict|licen[cs]/, which is right for findings and over-reaches "
                "on two house keys that must be written BEFORE the pixels. Renamed "
                "rather than worked around, and declared here."),
            "the_masks_are_the_hint": (
                "THE ONE THING A READER SHOULD CHECK FIRST. The two "
                "--ip-mask-capsules tokens were not typed: they are emitted by "
                "author_b08_openpose_hint.figure_capsules(stage()) -- one dilated "
                "capsule per limb of the SAME COCO-18 skeletons the hint PNG is "
                "drawn from, through the same LIMBS table. So the region each "
                "reference is applied to is, by construction, the region the "
                "ControlNet is steering, and the two cannot drift. Radii: 12 px on "
                "arms and legs, 30 on torso, 34 on head. THE 12 IS MEASURED: the "
                "guard's authored wrist (257.4,657.3) sits 27.6 px from the "
                "goblin's hanging arm, so two capsules stay disjoint while their "
                "radii sum under that -- disjoint through r=13, colliding at r=14. "
                "The hint's --selftest asserts the two figures' masks share no lit "
                "pixel while their bounding boxes DO overlap, which is the fact "
                "that makes rectangles impossible and capsules necessary."),
            "bar": {
                "b0_the_stack_is_what_it_claims": (
                    "VOID-CHECK, READ FIRST, THREE LINES. (i) preflight prints "
                    "`twins net verified: %d bytes, sha %s`; (ii) preflight prints "
                    "`staged driver, hint and BOTH references verified`; (iii) the "
                    "sidecar reads `ip_adapter_mask_geometry: capsules` and "
                    "`ip_adapter_masks_overlap: false` and names both reference "
                    "shas. Missing any of the three and the frame is void -- "
                    "\"the adapter did nothing\" and \"the adapter never loaded\" "
                    "are different findings." % (TWINS_BYTES, TWINS_SHA)),
                "b7_no_limb_fragmentation": (
                    "THIS RUNG'S OWN QUESTION, AND IT REPLACES THE HEAD-ONLY "
                    "INSTRUMENT, WHICH IS NOW A KNOWN TRAP.\n"
                    "INSTRUMENT: G-R sampled at SIX regions, three per figure -- "
                    "face, forearm, shin. Each box is placed ON THE DRAWN LIMB at "
                    "1:1 and its coordinates are published in the verdict, because "
                    "a box pinned to the authored keypoint measures whatever "
                    "happens to be there and cannot tell a mis-coloured limb from "
                    "an absent one. If a limb cannot be located within ~40 px of "
                    "its authored position, that is an adherence failure and the "
                    "region is reported UNMEASURABLE rather than scored.\n"
                    "PASSES IF each figure's WITHIN-FIGURE SPREAD (max minus min "
                    "across its three regions) is <= 25.0 levels. The parent "
                    "measured 106.8 for the guard (face -58.2, forearm +48.6) and "
                    "91.4 for the goblin (head +67.7, legs -23.7); both must "
                    "collapse. A figure whose three regions agree is one body.\n"
                    "AND THE SIGNS MUST BE RIGHT, or a frame with two identical "
                    "grey figures would pass: every guard region <= 0.0 and every "
                    "goblin region >= +20.0, the same two class boundaries this "
                    "beat has used since rung 1."),
                "b2_the_identities_separate": (
                    "CARRIED, AND NO LONGER THE HEADLINE. Guard face <= 0.0, "
                    "goblin face >= +20.0, separation >= +20.0. The parent already "
                    "passes this at +117.4 on these boxes WITHOUT any adapter, so a "
                    "pass here is expected and proves little on its own -- it is "
                    "scored to catch the adapter DRAGGING the two faces together, "
                    "which is the specific harm an unmasked reference would do."),
                "b4b_both_arms_stay_on_their_skeletons": (
                    "MUST SURVIVE -- this is what the parent bought and what an "
                    "adapter could plausibly spend. The guard's hand centroid "
                    "within ~60 px of the authored wrist (280.5,695.1); the parent "
                    "measured 52.5 px. The goblin's arm stays down, hands near "
                    "y~900 against an authored wrist of (221,857). The two hands "
                    "must not clasp."),
                "b4c_the_arm_belongs_to_the_guard": (
                    "MUST SURVIVE. The pointing arm grows from THE GUARD's "
                    "shoulder. Five mechanisms have held it; the uncontrolled tally "
                    "at this seed is 4 of 4 on the goblin. AND ITS SKIN MUST NOW "
                    "MATCH ITS OWNER, which is b7's business and is the whole "
                    "reason her mask was widened to enclose the limb."),
                "b1_the_pair": "TWO figures and only two, both whole in frame.",
                "b3_one_ground_plane": (
                    "Both stand on the same grass. The parent measured 34 px "
                    "between the two lowest skin rows; the ankles are not touched "
                    "by this rung, so a similar deviation is expected."),
                "b5_no_colossus": (
                    "Neither figure towers. The parent measured a ratio near 1.17 "
                    "against the authored 1.100."),
                "b6_drawn_not_traced": (
                    "Both read as drawn characters. The parent passed with the "
                    "pre-registered twins aesthetic cost -- looser linework, a "
                    "crude goblin face -- and it must not get WORSE. An adapter "
                    "carrying structure from a clean reference could plausibly "
                    "IMPROVE it, which would be a finding and not a win."),
                "b4a_board_down": (
                    "EXPECTED FAIL, PRE-REGISTERED, NOT THIS RUNG'S VARIABLE. No "
                    "object is in a pose hint. The remedy is multi-ControlNet "
                    "pose+scribble and it is the next rung after this one."),
            },
            "scoring_rule_pre_registered": (
                "THIS IS THE `verdict_rule`, WRITTEN BEFORE THE PIXELS, and all "
                "four branches close something. (1) If b7 passes on both figures "
                "AND B4b, B4c, B1, B3 and B5 all survive, the verdict is PASS and "
                "BEAT 08 HAS ITS PLATE RECIPE: staging, gesture and identity in one "
                "render, and the only clause left open is the board. (2) If b7 "
                "passes but a staging clause breaks, the adapter and the pose net "
                "COMPETE at ip-scale 0.7 and the next rung is one sample at a lower "
                "scale -- which clause broke names what the adapter overrode. (3) If "
                "the fragmentation SURVIVES inside the masks, then a per-region "
                "image condition does not govern skin tone at all, the cause is the "
                "checkpoint's own part-wise colour prior, and the next probe is a "
                "wording ablation rather than a stronger mask. (4) If the two "
                "figures come back matched but WRONG -- both human, or both green -- "
                "the masks are being applied in the wrong order or the positional "
                "zip is inverted, which is a driver bug and not a result; the "
                "sidecar's ref/mask pairing is read first to tell (3) from (4)."),
            "not_done_on_purpose": (
                "ONE sample, ONE arm, ONE variable. No ip-scale sweep (0.7 is the "
                "value that worked first try on the contour and a second value "
                "would need its own question), no second seed, no re-authored hint, "
                "no re-staged arm, no conditioning-scale change, no multi-ControlNet, "
                "no board, no night or colour-cast fix, no pick, no plate_ack waiver "
                "and no canon filename. The purple cast the parent returned is NOT "
                "addressed and is expected to persist."),
            "rights_and_weights": (
                "THIS IS THE `licence_note`. Clean. Base "
                "cagliostrolab/animagine-xl-3.1 (CreativeML Open RAIL++-M). "
                "ControlNet xinsir/controlnet-openpose-sdxl-1.0 twins variant, "
                "apache-2.0, no attribution condition, allowlisted in the driver by "
                "its upstream repo, blob name and digest. IP-Adapter h94/IP-Adapter, "
                "apache-2.0. Both references are repo-internal crops with no "
                "external image's terms attached. The hint is authored in PIL -- no "
                "annotator, so the lllyasviel/Annotators landmine is untouched."),
        },
    )

    # ---- the identity arguments, appended to the render step. The ORDER IS
    # ---- LOAD-BEARING: --ip-ref and --ip-mask-capsules are zipped positionally,
    # ---- so swapping a line would hand each figure the other's identity and the
    # ---- frame would look like the mechanism inverting rather than like the
    # ---- argv being wrong. GOBLIN FIRST, exactly as ep2-b08-ipamask-0819 had it.
    # The render step's NAME is renamed here rather than by a retoken pair: a
    # bare ("twins" -> "twinsipa") substitution would also rewrite
    # `cnet-openpose-twins` into a directory that does not exist, and the
    # preflight's own message text with it. Explicit beats clever.
    step = [s for s in child["steps"] if s["name"] == "twins"][0]
    step["name"] = "twinsipa"
    i = step["argv"].index("--prompt-file")
    step["argv"][i:i] = [
        "--ip-ref", REF_GOBLIN,
        "--ip-mask-capsules", CAPS_GOBLIN,
        "--ip-ref-sha256", REF_GOBLIN_SHA,
        "--ip-ref", REF_GUARD,
        "--ip-mask-capsules", CAPS_GUARD,
        "--ip-ref-sha256", REF_GUARD_SHA,
        "--ip-scale", IP_SCALE,
    ]

    # ---- the preflight now checks four staged files, not two.
    child["steps"][0]["argv"][2] = PREFLIGHT
    # ---- and the publish step must carry the references across with the frame.
    pub = [s for s in child["steps"] if s["name"] == "publish"][0]
    pub["argv"][2] = pub["argv"][2].replace(
        'glob.glob(ctl_dir + "/b08-openpose-nat-0819.png")',
        'glob.glob(ctl_dir + "/b08-openpose-nat-0819.png")\n'
        '               + glob.glob(ctl_dir + "/b08-ref-*-0819.png")')
    pub["argv"][2] = pub["argv"][2].replace("len(files) >= 5", "len(files) >= 7")

    # ---- assertions. Every one is a way a "one variable" rung has silently
    # ---- become something else before.
    argvs = [str(a) for s in child["steps"] for a in s["argv"]]
    flat = derive_spec._dump({k: v for k, v in child.items()
                              if k not in ("derivation", "who_ruled_this_rung")})

    def flag(n):
        return [argvs[i + 1] for i, v in enumerate(argvs) if v == n]

    assert flag("--control") == [HINT], flag("--control")
    assert flag("--control-sha256") == [HINT_SHA]
    assert flag("--scale") == ["1.0"], flag("--scale")
    assert flag("--seed") == ["20260819"], flag("--seed")
    assert flag("--controlnet") == [TWINS_DIR]
    assert flag("--arm") == ["twinsipa"], flag("--arm")
    assert flag("--repo-commit") == [REPO_COMMIT]
    assert flag("--root") == [STAGE], flag("--root")
    assert flag("--ip-ref") == [REF_GOBLIN, REF_GUARD], flag("--ip-ref")
    assert flag("--ip-ref-sha256") == [REF_GOBLIN_SHA, REF_GUARD_SHA]
    assert flag("--ip-mask-capsules") == [CAPS_GOBLIN, CAPS_GUARD]
    assert flag("--ip-scale") == [IP_SCALE]
    assert "--ip-mask" not in argvs, "a rect mask leaked into a capsule job"
    assert PARENT_ID not in flat, "parent id survived"
    assert [s["name"] for s in child["steps"]] == ["preflight", "twinsipa",
                                                   "publish"]
    # the words are the parent's, character for character
    pp = {os.path.basename(k.replace("\\", "/")): v for k, v in parent["payload"].items()}
    cp = {os.path.basename(k.replace("\\", "/")): v for k, v in child["payload"].items()}
    assert pp == cp, "payload text drifted from the parent's"

    # AND THE MASKS ARE ACTUALLY DISJOINT -- asserted here, on the exact strings
    # that will be in the argv, not merely trusted from the hint's selftest.
    import controlnet_plate as cp_mod
    mg = cp_mod.capsule_mask(cp_mod.parse_capsules(CAPS_GUARD, 832, 1216), 832, 1216)
    mb = cp_mod.capsule_mask(cp_mod.parse_capsules(CAPS_GOBLIN, 832, 1216), 832, 1216)
    assert not cp_mod.masks_overlap(mg, mb), "the two masks in this argv OVERLAP"
    assert cp_mod.rects_overlap(mg.getbbox(), mb.getbbox()), \
        "the bounding boxes do NOT overlap -- then rects would have done, and " \
        "this job's whole justification is wrong"

    out = derive_spec.write(child, OUT)
    print("parent    %s" % SRC)
    print("child     %s" % os.path.relpath(out, derive_spec.REPO))
    print("variable  + two masked references at ip-scale %s (capsule masks)" % IP_SCALE)
    print("held      twins net, hint %s, scale 1.0, seed 20260819, words" % HINT_SHA[:8])
    print("masks     guard %d capsules / goblin %d capsules, from stage()"
          % (len(cp_mod.parse_capsules(CAPS_GUARD, 832, 1216)),
             len(cp_mod.parse_capsules(CAPS_GOBLIN, 832, 1216))))
    print("          lit pixels disjoint; bounding boxes overlap (rects impossible)")
    print("steps     %s" % " -> ".join(s["name"] for s in child["steps"]))
    print()
    print("NOT ENQUEUED. Stage 4 files to %s then:" % STAGE)
    print("  python3 pipeline/box_enqueue.py pipeline/jobs/%s.yaml --backlog" % NEW_ID)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
