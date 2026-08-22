#!/usr/bin/env python3
r"""THE GOBLIN, ROUND TWO: HIS PIXELS AS THE INIT *AND* A SKELETON TELLING THEM
WHERE TO SIT.

WHAT ROUND ONE BOUGHT AND WHAT IT COULD NOT. `ep2-b13-i2icanon-*-0822` put the
founder's own picture in as the INIT instead of through an encoder, and his eye
reached the output for the first time in sixteen rounds. It also measured the
ceiling: the face breaks between 0.40 and 0.45. And it recorded, in advance and
on purpose, the one thing it did not test -- at 0.30-0.45 the init owns the
composition, so the figure is still STANDING and beat 13 is SEATED. Round one's
own `round_2_lever` names this cell: "THE FACE HOLDS AND THE POSE IS WRONG ->
ControlNet at the winning strength, skeleton from jerry_canon_0821."

NO NEW PIPELINE WAS COMPOSED, AND THAT IS THE HEADLINE OF THIS ROUND'S BUILD.
The brief said no repo tool does init + ControlNet together. It was already
false. `inpaint_fruit.py` has taken ControlNet hints inside an SDXL inpaint
pipeline since 2026-08-20, and round one had already established that an
ALL-WHITE mask on base weights (unet.in_channels=4) turns that pipeline into
plain img2img. Put those two facts together and
`StableDiffusionXLControlNetInpaintPipeline` at `--pad-crop 0` on a full-frame
mask IS img2img-plus-ControlNet. Round two is round one's command line with four
flags added. A fourth model-loading script was not written.

THE ONE THING THAT WAS MISSING WAS A GUARD, AND IT IS NOW IN THE DRIVER.
`b08-arm-route-0819.md` section 28 measured why the earlier ControlNet-inside-
inpaint attempt produced the worst frame on that route: `padding_mask_crop`
derives ONE crop box from the mask and applies it to the init, the mask AND
every hint, then resizes all of them back up -- so an authored two-figure hint
arrived as one torso filling the frame at 3.07x, a different instruction, which
the sampler faithfully obeyed while every automatic clause passed it. Its last
paragraph states the rule and nothing enforced it. `assert_hint_survives_crop`
now refuses that configuration with rc 15. It measures the MAGNIFICATION rather
than banning the flag, so this route -- full-frame mask, `--pad-crop 0`, hint at
1.0x -- is admitted by construction and cannot drift into the defect.

THE SKELETON IS NOT NEW WORK EITHER. `jerry-canon-h37fsit-0821.png` is beat 13's
seated pose authored at head_frac 0.370 -- the proportion `jerry_canon_0821`
MEASURED off the founder's own image (head 337 px, figure 912 px, 2.71 heads).
It is the hint the whole b13 canon wave used, pinned at sha 3db75427, 832x1216,
the init's exact size. So the hint and the init are the same character at the
same scale in the same frame, and the ONLY disagreement between them is the one
this sample is asking about: standing versus seated. Its net,
`xinsir/controlnet-openpose-sdxl-1.0` at scale 1.0, is the pair the canon wave
already demonstrated binds a pose.

WHY THE BRACKET STOPS AT 0.40. Round one measured the face breaking between 0.40
and 0.45, so 0.45 is out and 0.40 is the ceiling cell, not a comfortable one.
The variable is the strength and only the strength: 0.30 / 0.35 / 0.40, with the
net, the hint, the scale, the seed, the prompt, the negative and every sampler
number byte-identical across the three.

  python3 pipeline/derive_goblin_i2icnet_0822.py            # dry
  python3 pipeline/derive_goblin_i2icnet_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec            # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77  # noqa: E402
from derive_goblin_i2i_0822 import assert_no_face_terms    # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# THE PARENT IS ROUND ONE'S OWN CELL, so the diff between the two specs is
# readable as exactly what changed: four flags and a strength.
PARENT = "pipeline/jobs/ep2-b13-i2icanon-s30-0822.yaml"
PARENT_DIRTOK = "b13i2icanon-s30-0822"
PARENT_OUTTOK = "b13-i2icanon-s30"
# Two tokens round one inherited from ITS parent and never cleaned: the publish
# directory still ended `-r2-0820` (beat 16's sapcomp round two) and the render
# step was named for a seed the job does not use. Both are retokened here so the
# artifacts of this round are not filed under two other rounds' numbers.
PARENT_STALE_R2 = "-r2-0820"
PARENT_STALE_SEED = "s20260820"

CANON = "taste/refs/goblin-canon-founder-0821.png"
CANON_SHA = "b62f333644c2f3161c0d5933f122f32c46c7608d1a97f758f3c53e4692eb4f00"
MASK_DIR = "farm-out/ep2-goblin-i2i-src-0822"
MASK = "fullframe-mask-0822.png"

# BEAT 13'S SEATED SKELETON, AT THE FOUNDER'S OWN MEASURED PROPORTION.
HINT_REPO_PATH = "farm-out/jerry-canon-assets-0821/jerry-canon-h37fsit-0821.png"
HINT = "jerry-canon-h37fsit-0821.png"
HINT_SHA = "3db75427b2696b3beafd3c665281bfcfaa84ae03d7e35d51ee1257abbcd77b0e"
NET = "xinsir/controlnet-openpose-sdxl-1.0"
SCALE = "1.0"

SEED = 20260823          # round one's seed, so the two rounds are comparable
SEED_TOK = "s20260823"

BEAT = 13

# cell -> (strength, why this cell)
CELLS = {
    "s30": ("0.30",
            "ROUND ONE'S FLOOR, AND THE ONLY CELL THAT IS A CLEAN A/B. At this "
            "exact strength, seed and wording round one produced a frame whose "
            "face passed and whose pose did not move at all. This cell differs "
            "from that filed frame by the ControlNet and NOTHING else, so "
            "whatever the pose does here is the net's doing and cannot be "
            "attributed to denoising more."),
    "s35": ("0.35",
            "THE MIDDLE, AND IT IS NEW GROUND -- round one bracketed 0.30, "
            "0.40, 0.45 and never rendered 0.35. If the face survives at 0.40 "
            "this cell is redundant; if it does not, this is the one that says "
            "whether there is any room at all between a face that holds and a "
            "pose that moves."),
    "s40": ("0.40",
            "THE CEILING, AND IT IS THE LAST SAFE CELL RATHER THAN A "
            "COMFORTABLE ONE. Round one measured the face breaking between "
            "0.40 and 0.45, so this is the most denoising the route may buy. "
            "0.45 is deliberately NOT rendered: it is on the far side of a "
            "measured break and re-testing it would spend a rung on a known "
            "answer."),
}

# ROUND ONE'S PROMPT, UNCHANGED, TO THE BYTE. Changing the words in the same
# round that adds the net would make this two variables, and the words are
# already the founder's own approved shots.md wording for beat 13. The identity
# clause is absent for the same reason it was absent in round one: his face is
# the INIT, and re-describing it is what the closure forbids.
PROMPT = ("a small green goblin sitting in tall grass, hands clasped between "
          "knees, head tipped sideways, resting, detailed cinematic anime, "
          "masterpiece, best quality, very aesthetic")

NEGATIVE = ("lowres, worst quality, low quality, text, watermark, "
            "photorealism, 3d render, blurry, 2boys, multiple heads")

BAR = """TWO CLAUSES, AND THEY ARE SCORED SEPARATELY BECAUSE THE WHOLE POINT OF
THIS ROUND IS TO FIND OUT WHETHER THEY CAN BOTH BE TRUE AT ONCE.

THE EYE IS THE CLAUSE. Read at 1:1 against
`taste/refs/goblin-canon-founder-0821.png` and nothing else -- not tile B, not
round one, not a metric.

  E1 THE EYE. Narrow almond, off-white field, a TINY dark pupil, heavy upper
     lid. Four vetoes were spent on this axis. A large round iris of any colour
     is a FAIL.
  E2 THE SKULL AND EARS. Broad low dome; smallish pointed ears NEAR HORIZONTAL,
     not swept up and back.
  E3 THE FACE IS SMOOTH. No brow furrows, no folds, no jowls.
  E4 PALETTE. Desaturated sage, washed and high-key -- not saturated kelly.
  E5 COSTUME. The shirt with its placket, dark shorts, dark boots.

THE POSE IS THE NEW CLAUSE, AND IT IS THE REASON THIS ROUND EXISTS.

  P1 IS HE SEATED? Hips down, knees up and apart, feet on the ground plane --
     the skeleton's stance. STILL STANDING is the null result for this round,
     exactly as it was the expected result for round one.
  P2 DID HE ADOPT THE SKELETON OR JUST BEND? Compare against
     `farm-out/jerry-canon-assets-0821/jerry-canon-h37fsit-0821.png`. A crouch
     that is not the authored stance is partial adoption and should be reported
     as partial, not rounded up to a pass.
  P3 HANDS CLASPED BETWEEN THE KNEES, which is both the skeleton's wrist
     placement and the founder's own wording for the beat.

AND THE JOINT CLAUSE, WHICH IS THE VERDICT:

  J1 DO E1-E5 AND P1 HOLD IN THE SAME FRAME? A frame that is seated with a
     stranger's face is a FAIL. A frame with his face still standing is a FAIL
     for this round (it was a PASS for round one). Only both is the route."""

PREDICTED = """FIRST, AND IT IS THE MOST LIKELY: THE POSE DOES NOT MOVE AT 0.30.
At strength 0.30 the pass runs 12 of 40 steps from a latent that already holds a
standing figure, and a ControlNet residual has to overcome that latent rather
than a random one. The net may simply not have enough denoising left to relocate
a body. If 0.30 is standing and 0.40 is seated, the crossing point IS the
finding and the route's operating number.

SECOND, AND IT IS THE ONE THAT WOULD CLOSE THE ROUTE HONESTLY: THE TWO CURVES DO
NOT OVERLAP. The face holds below ~0.40 and the pose only adopts above it. That
is not a failure to fix by trying harder -- it is a measured statement that
init-carried identity and hint-carried pose want opposite ends of the same
knob, and the answer becomes a LoRA trained on his pixels, which round one
already named as the durable fix. If this is what the frames say, it gets
reported as a tension with both curves, not as "needs another round".

THIRD: A HYBRID THAT IS WORSE THAN EITHER. The figure half-relocates -- a
standing body with the knees of a seated one, or a second pair of legs. This is
the classic low-strength ControlNet artifact and it would show up as P2 partial
with E1 still passing.

WHAT WOULD SURPRISE ME: a clean seated figure at 0.30 with the eye intact. That
would mean spatial conditioning reaches through a low-strength init far more
cheaply than the composition work on this route has ever suggested, and it would
make every remaining goblin beat a plate derive rather than a research round."""


def main() -> int:
    write = "--write" in sys.argv

    def sha_of(rel):
        return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()

    for rel, want, what in ((CANON, CANON_SHA, "the canon image"),
                            (HINT_REPO_PATH, HINT_SHA, "the seated skeleton")):
        if not os.path.isfile(os.path.join(REPO, rel)):
            print("!! %s missing: %s" % (what, rel))
            return 1
        have = sha_of(rel)
        if have != want:
            print("!! %s hashes %s, spec says %s" % (what, have, want))
            return 1

    mask_rel = "%s/%s" % (MASK_DIR, MASK)
    if not os.path.isfile(os.path.join(REPO, mask_rel)):
        print("!! %s missing" % mask_rel)
        return 1
    mask_sha = sha_of(mask_rel)

    # THE HINT AND THE INIT MUST BE THE SAME FRAME. The driver refuses a
    # mismatch with rc 13 on the card; refusing it HERE means the spec is never
    # written at all, which is cheaper and louder.
    from PIL import Image
    isz = Image.open(os.path.join(REPO, CANON)).size
    hsz = Image.open(os.path.join(REPO, HINT_REPO_PATH)).size
    if isz != hsz:
        print("!! init is %dx%d and the hint is %dx%d -- a hint in another "
              "coordinate system is a skeleton landing off the figure."
              % (isz + hsz))
        return 1

    for cell in sorted(CELLS):
        strength, cell_why = CELLS[cell]
        new_id = "ep2-b13-i2icnet-%s-0822" % cell
        dirtok = "b13i2icnet-%s-0822" % cell
        outtok = "b13-i2icnet-%s" % cell
        init_name = "goblin-canon-founder-0821.png"
        farm = lambda n: r"C:\banyan-farm\%s\%s" % (dirtok, n)  # noqa: E731

        np_ = assert_under_clip77("%s prompt" % new_id, PROMPT)
        nn_ = assert_under_clip77("%s negative" % new_id, NEGATIVE)

        fetch = '''#!/usr/bin/env python3
"""Fetch THE CANON IMAGE as this job's init, the full-frame mask that makes the
inpaint pipeline behave as img2img, and THE SEATED SKELETON that is the whole
point of round two. All three by sha256, all three refused on any mismatch.

The init is taste/refs/goblin-canon-founder-0821.png -- the picture the founder
selected with "dude, this is how the goblin should look". The hint is beat 13's
seated pose authored at the head_frac measured off that same picture, and it is
the hint the b13 canon wave already ran."""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\%s"
BASE = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
UA = {"User-Agent": "banyan-city-i2icnet/1.0 (albert.numbro@gmail.com)"}
WANT = {
    "%s": ("%s", "%s"),
    "%s": ("%s", "%s"),
    "%s": ("%s", "%s"),
}

os.makedirs(OUT, exist_ok=True)
for name, (path, want) in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(BASE + path, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing.\\n   want %%s\\n   have %%s"
                 %% (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%s %%d bytes sha %%s OK" %% (name, len(raw), have), flush=True)
''' % (dirtok, init_name, CANON, CANON_SHA, MASK, mask_rel, mask_sha,
       HINT, HINT_REPO_PATH, HINT_SHA)

        note = (
            "IMG2IMG FROM THE CANON IMAGE *PLUS* A POSE NET, cell %s, strength "
            "%s. The mask is FULL FRAME (all white) and --pad-crop is 0, which "
            "together turn the SDXL ControlNet-inpaint pipeline on base weights "
            "into img2img-with-a-hint: the whole frame is denoised from a latent "
            "that still carries the founder's own picture, while "
            "%s at %s conditions where the body goes. PAD-CROP MUST STAY 0. "
            "b08-arm-route-0819.md section 28 measured that padding_mask_crop "
            "rescales the hint along with the init -- alignment stays exact and "
            "the conditioning becomes a different instruction. The driver now "
            "refuses that combination (rc 15); at 0 the magnification is 1.0 and "
            "the defect cannot occur." % (cell, strength, NET, SCALE))

        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "the goblin img2img lane, 2026-08-22",
                "consumer": (
                    "THE FOUNDER. Round one put his eye in an output for the "
                    "first time in sixteen rounds and left one question open: "
                    "at a strength low enough to keep his face, the init owns "
                    "the composition and the figure will not move. Beat 13 is "
                    "SEATED. This cell (%s) asks whether a skeleton can move "
                    "the body while his face survives. If yes, this is the "
                    "plate route for every goblin beat and b13+b14 derive "
                    "immediately. If no, the face-versus-pose tension is "
                    "measured on both curves and the next move is a LoRA on "
                    "his pixels." % cell),
                "success": (
                    "ONE 832x1216 png at strength %s in which E1-E5 hold "
                    "against his image at 1:1 AND P1 says he is seated. Both "
                    "halves in the SAME frame (J1). A seated stranger is a "
                    "fail; his face still standing is a fail for this round."
                    % strength),
                "why": (
                    "ROUND TWO: THE INIT KEEPS THE FACE, THE NET MOVES THE "
                    "BODY. %s\n\n"
                    "NO NEW TOOL. inpaint_fruit.py has taken ControlNet hints "
                    "inside an SDXL inpaint pipeline since 2026-08-20, and "
                    "round one established that an all-white mask on base "
                    "weights makes that pipeline plain img2img. Together, at "
                    "--pad-crop 0, that IS img2img plus ControlNet. This spec "
                    "is round one's command line with four flags added.\n\n"
                    "THE CLOSURE STILL HOLDS. No face tag, no IP-Adapter, no "
                    "reference re-crop -- there is no IP-Adapter anywhere in "
                    "this spec and the negative carries no face term at all. "
                    "A skeleton is not a face tag: it says where the body is, "
                    "and it says nothing about his eye." % cell_why),
            },
            overrides={
                "key:node": "002b-first-citizen",
                "key:beat": BEAT,
                "key:priority": 2,
                "key:est_minutes": 4,
                "key:sample": True,
                # NO prompt.txt / negative.txt OVERRIDE, AND THAT IS THE POINT:
                # they are byte-identical to round one on purpose, so that the
                # strength and the net are the only things that moved.
                # derive_spec refuses a no-op override, which is why they are
                # ASSERTED below against the inherited payload instead.
                "payload:fetch_init.py": fetch,
                # THE DRIVER GOES UP FRESH, because the guard this round relies
                # on was added to it today. derive_spec refuses a payload
                # override that is byte-identical to the parent's, so this line
                # failing would itself be the proof the guard did not travel.
                "payload:inpaint_fruit.py": open(
                    os.path.join(REPO, "pipeline/inpaint_fruit.py"),
                    encoding="utf-8").read(),
                "argv:--seed": str(SEED),
                "argv:--strength": strength,
                "argv:--init-sha256": CANON_SHA,
                "argv:--pad-crop": "0",
                "argv:--note": note,
            },
            retoken=[(PARENT_DIRTOK, dirtok),
                     (PARENT_OUTTOK, outtok),
                     (PARENT_STALE_R2, "-0822"),
                     (PARENT_STALE_SEED, SEED_TOK)],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "is_candidate": True,
                "the_one_variable": (
                    "THE STRENGTH, %s. Across the three cells the init, the "
                    "mask, the hint, the net, the conditioning scale (%s), the "
                    "prompt, the negative, the seed (%d) and every sampler "
                    "number are identical."
                    % (strength, SCALE, SEED)),
                "the_rung_this_is_one_variable_from": (
                    "ep2-b13-i2icanon-%s-0822, ROUND ONE'S CELL OF THE SAME "
                    "NAME -- for s30 and s40 that is a filed, rendered frame at "
                    "the identical strength, seed and wording, and the only "
                    "difference is the ControlNet. That makes the pose "
                    "attributable to the net rather than to denoising more. "
                    "(s35 has no round-one twin; it is new ground between two "
                    "measured points.)" % cell),
                "the_hint": (
                    "%s, sha %s, 832x1216 -- THE INIT'S EXACT SIZE, which the "
                    "driver asserts before a weight loads (rc 13). It is beat "
                    "13's seated pose authored at head_frac 0.370, the "
                    "proportion jerry_canon_0821 measured off the founder's own "
                    "image (head 337 px, figure 912 px, 2.71 heads), and it is "
                    "the hint the entire b13 canon wave ran. Net %s at scale "
                    "%s, the pair that wave demonstrated binds a pose. Neither "
                    "the hint nor the net is new work in this round."
                    % (HINT, HINT_SHA[:16], NET, SCALE)),
                "pad_crop_is_zero_and_that_is_load_bearing": (
                    "b08-arm-route-0819.md section 28: padding_mask_crop "
                    "derives ONE crop box from the mask and applies it to the "
                    "init, the mask AND every hint, then resizes all of them "
                    "back to model resolution. On a small mask that magnified "
                    "an authored two-figure hint 3.07x into one torso filling "
                    "the frame -- the alignment stayed exact, the instruction "
                    "changed, the sampler obeyed it, and every automatic clause "
                    "passed the worst frame on that route. Section 28 wrote the "
                    "rule in prose and nothing enforced it. It is now "
                    "inpaint_fruit.assert_hint_survives_crop, which measures "
                    "the magnification rather than banning the flag: this "
                    "route's full-frame mask magnifies by 1.0 and is admitted, "
                    "a small region is refused with rc 15."),
                "route_closure": (
                    "pipeline/canon.yaml `route_closure_2026_08_22`. No face "
                    "tag, no IP-Adapter scale, no reference re-crop. This spec "
                    "has no IP-Adapter at all -- round one's parent chain "
                    "dropped it and it does not come back -- and the face-term "
                    "ban is asserted in code against both the positive and the "
                    "negative before the spec is written."),
                "clip77_measured_not_estimated": (
                    "positive %d of 77, negative %d of 77, on animagine's own "
                    "vocab." % (np_, nn_)),
                "round_3_lever": (
                    "NAMED BEFORE THE RENDER, in order:\n"
                    "  1. FACE HOLDS, POSE DOES NOT MOVE AT ANY CELL -> the "
                    "next knob is the CONDITIONING SCALE, not the strength: "
                    "the net is at 1.0 and there is nowhere up, so the honest "
                    "read is that a low-strength init cannot be overruled and "
                    "the answer is a LoRA on his pixels.\n"
                    "  2. FACE HOLDS AND POSE ADOPTS -> THIS IS THE PLATE "
                    "ROUTE. Stage the sheet for the founder and derive b13 and "
                    "b14 as the first pair, same recipe, beat-specific "
                    "skeletons from the same h37f family.\n"
                    "  3. POSE ADOPTS ONLY WHERE THE FACE BREAKS -> report both "
                    "curves and STOP. That is a measured tension, not a round "
                    "to retry, and it is round one's own fail mode three.\n"
                    "At most one more round before this goes back to the "
                    "founder either way."),
                "post_ship_patch": (
                    "review/ep2-ship-0821 IS NOT TOUCHED. These are samples of "
                    "a ROUTE, not plate candidates for any beat."),
            },
            by="pipeline/derive_goblin_i2icnet_0822.py")

        # ---- THE FOUR FLAGS. derive_spec's argv override can only REPLACE a
        # flag the parent already has, and round one has no ControlNet -- so the
        # flags are inserted here and then asserted, rather than assumed.
        for st in child["steps"]:
            if st.get("name") in ("dry", SEED_TOK):
                st["argv"] = [str(x) for x in st["argv"]] + [
                    "--controlnet", NET,
                    "--control", farm(HINT),
                    "--control-sha256", HINT_SHA,
                    "--scale", SCALE]

        # ---- the hint travels home with the frame, or the run is unreproducible
        pubs = [st for st in child["steps"] if st.get("name") == "publish"]
        if len(pubs) != 1:
            raise SystemExit("!! %s has %d publish steps" % (new_id, len(pubs)))
        pv = pubs[0]["argv"]
        marker = '    "%s",\n' % MASK
        body = pv[-1]
        if marker not in body:
            raise SystemExit("!! %s: cannot find the mask in the publish NAMES "
                             "list, so the hint has nowhere to be added" % new_id)
        pv[-1] = body.replace(marker, marker + '    "%s",\n' % HINT, 1)

        # THE STALE-TOKEN SWEEP IS OVER STRUCTURE, NOT PROSE. A path, a step or
        # an artifact still carrying the parent's token would write this round's
        # output into round one's directory, which is the failure this checks
        # for. The narrative fields legitimately CITE round one by job id --
        # `the_rung_this_is_one_variable_from` names it on purpose -- so sweeping
        # them too would forbid saying what this rung is one variable from.
        structural = repr({k: child.get(k) for k in
                           ("payload", "steps", "artifacts")})
        for tok in (PARENT_DIRTOK, PARENT_OUTTOK, PARENT_STALE_R2,
                    PARENT_STALE_SEED):
            if tok in structural:
                raise SystemExit("!! %s: a path, step or artifact still names "
                                 "the parent's %r" % (new_id, tok))
        names = [st["name"] for st in child["steps"]]
        if names.count("fetch") != 1:
            raise SystemExit("!! %s has %d fetch steps"
                             % (new_id, names.count("fetch")))

        pay = child["payload"][farm("prompt.txt")]
        neg = child["payload"][farm("negative.txt")]
        assert_no_face_terms(new_id, pay, neg)
        # INHERITED, NOT RE-TYPED. The words are round one's to the byte; if the
        # parent's ever drift from what this file documents, that is a silent
        # second variable and the spec is not written.
        if pay.strip() != PROMPT or neg.strip() != NEGATIVE:
            raise SystemExit(
                "!! %s: the inherited prompt/negative are not round one's.\n"
                "   prompt : %r\n   want   : %r\n   negative: %r\n   want    : %r"
                % (new_id, pay.strip(), PROMPT, neg.strip(), NEGATIVE))

        # THE DRIVER THAT TRAVELS MUST BE THE GUARDED ONE. A spec that carried
        # the pre-2026-08-22 driver would run this recipe with nothing enforcing
        # section 28, which is the whole reason the guard was written.
        drv = child["payload"][farm("inpaint_fruit.py")]
        for needle in ("assert_hint_survives_crop", "HINT_MAGNIFICATION_CEILING",
                       "def hint_magnification"):
            if needle not in drv:
                raise SystemExit("!! %s: the driver payload has no %r -- the "
                                 "section 28 guard did not travel to the box"
                                 % (new_id, needle))

        # ---- every flag this round adds, verified in the argv that will run
        gpu = [st for st in child["steps"] if st.get("name") == SEED_TOK]
        if len(gpu) != 1:
            raise SystemExit("!! %s: expected one render step named %s, got %d"
                             % (new_id, SEED_TOK, len(gpu)))
        for st in child["steps"]:
            if st.get("name") not in ("dry", SEED_TOK):
                continue
            argv = [str(t) for t in st["argv"]]
            for flag, wantv in (("--strength", strength), ("--pad-crop", "0"),
                                ("--init-sha256", CANON_SHA),
                                ("--seed", str(SEED)),
                                ("--controlnet", NET),
                                ("--control", farm(HINT)),
                                ("--control-sha256", HINT_SHA),
                                ("--scale", SCALE)):
                if argv.count(flag) != 1:
                    raise SystemExit("!! %s step %s: %s appears %d times"
                                     % (new_id, st["name"], flag,
                                        argv.count(flag)))
                got = argv[argv.index(flag) + 1]
                if got != wantv:
                    raise SystemExit("!! %s step %s: %s is %r want %r"
                                     % (new_id, st["name"], flag, got, wantv))
            # PAD-CROP 0 IS THE CLAUSE THAT KEEPS SECTION 28 IMPOSSIBLE, and a
            # ControlNet spec that let it be anything else would be the defect
            # re-authored rather than re-discovered.
            if argv[argv.index("--pad-crop") + 1] != "0":
                raise SystemExit("!! %s: --pad-crop must be 0 on a hinted run"
                                 % new_id)

        out = "pipeline/jobs/%s.yaml" % new_id
        if write:
            derive_spec.write(child, out)
            print("wrote %s   strength=%s  net=%s@%s" % (out, strength, NET, SCALE))
        else:
            print("%-30s strength=%-5s hint=%s scale=%s clip77 %d/%d"
                  % (new_id, strength, HINT[:28], SCALE, np_, nn_))
    if not write:
        print("\n-- dry run, %d cell(s). re-run with --write." % len(CELLS))
        print("   init  : %s" % CANON)
        print("   hint  : %s (%s)" % (HINT_REPO_PATH, HINT_SHA[:16]))
        print("   net   : %s at scale %s, --pad-crop 0" % (NET, SCALE))
        print("   prompt: %s" % PROMPT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
