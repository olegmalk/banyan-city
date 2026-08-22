#!/usr/bin/env python3
r"""THE GOBLIN, ROUND ONE OF THE ROUTE THAT REPLACES SIXTEEN: IMG2IMG FROM HIS
OWN IMAGE.

WHY THE OLD ROUTE IS GONE. The founder vetoed all four eye rounds including
r11a -- "these are not my goblin" -- which is the fourth veto on this axis and
lands on roughly sixteen rounds of face work. Every one of them moved WORDS or
moved the IP-ADAPTER. `pipeline/canon.yaml` `route_closure_2026_08_22` and
`pipeline/work-ladder-0819.md` record the closure: no rung on this character
may be spent on a face tag, an IP-Adapter scale, or a reference re-crop, ever
again.

WHY IT COULD NOT HAVE WORKED, and the ladder measured this without reading it.
An IP-Adapter reference is ENCODED -- CLIPImageProcessor resizes to 224 and
centre-crops -- so his face arrives as a few hundred embedding tokens and the
denoiser then RESOLVES a face out of animagine's own prior. Round nine's own
numbers: at sq65 (58.9% of the frame encoded) the eye came back a green anime
iris; at sq45 (28.3%) it came back closer. LESS of his face reaching the
encoder produced MORE of his face in the output. That is not a knob with a
better setting further along; it is a route whose target is unreachable.

WHAT THIS DOES INSTEAD. HIS PIXELS ENTER AS PIXELS.
`taste/refs/goblin-canon-founder-0821.png` is the INIT, not the reference, and a
low-strength pass FINISHES it rather than inventing a face. That is exactly the
relationship the 0.30 sapling pass has to its drawn plant, and it is the same
instrument: `inpaint_fruit.py`, unchanged, which has now carried six composited
objects and 59 dataset frames without once losing the thing it was handed.

THE MASK IS FULL-FRAME AND THAT IS WHAT MAKES IT IMG2IMG. `inpaint_fruit.py`
runs StableDiffusionXLInpaintPipeline on BASE weights (unet.in_channels=4), and
with an all-white mask that is plain img2img at the given strength: the whole
frame is denoised from a latent that still carries his drawing. `--pad-crop 0`
because padding_mask_crop exists to zoom a SMALL mask to model resolution and
there is nothing to zoom when the mask is the frame.

NO NEW TOOL IS WRITTEN, ON PURPOSE. The temptation was a fresh
StableDiffusionXLImg2ImgPipeline script. It would have been the fourth
model-loading script in this repo and the first one never sha-guarded, never
provenance-writing and never run. `inpaint_fruit.py` already verifies its init
against `--init-sha256` before loading a weight, already writes the §7.2
sidecar, and already refuses on a mismatch -- all three of which this route
needs more than the old one did, because the init IS the canon now.

THE BRACKET IS THE SAMPLE. Three cells, one variable, strength 0.30 / 0.40 /
0.45 -- the coordinator's bracket -- plus a fourth at 0.55 marked as a PROBE
and not a candidate, because the bracket alone cannot say where the face breaks
and a route needs its ceiling measured once.

WHAT THIS ROUND DELIBERATELY DOES NOT TEST: THE POSE. His image is a standing
figure and beat 13 is seated, and at 0.30-0.45 the init owns the composition --
the pose will not move and is not expected to. That is the correct order:
if his face does not survive a low-strength pass, no skeleton will rescue it,
and round two adds ControlNet only if round one holds. Saying so now means a
round-one output that is still standing is a PASS on what was asked and not a
surprise.

  python3 pipeline/derive_goblin_i2i_0822.py            # dry
  python3 pipeline/derive_goblin_i2i_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec            # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77  # noqa: E402
import jerry_canon_0821 as C  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b16-sapcomp-r2-0820.yaml"
PARENT_DIRTOK = "b16sapcomp-r2-0820"
PARENT_OUTTOK = "b16-sapcomp"
PARENT_MASKTOK = "16-why-sapcomp-mask-0820"
PARENT_INITTOK = "16-why-sapcomp-0820"

CANON = "taste/refs/goblin-canon-founder-0821.png"
CANON_SHA = "b62f333644c2f3161c0d5933f122f32c46c7608d1a97f758f3c53e4692eb4f00"
MASK_DIR = "farm-out/ep2-goblin-i2i-src-0822"
MASK = "fullframe-mask-0822.png"
SEED = 20260823   # the canon wave's seed, so this is comparable to w4/w7a

BEAT = 13

# cell -> (strength, is_candidate, why this cell)
CELLS = {
    "s30": ("0.30", True,
            "The floor, and the same number the sapling composites use. If his "
            "face does not survive HERE it survives nowhere, and the route is "
            "dead in one cell."),
    "s40": ("0.40", True,
            "The middle of the bracket. Enough denoising to move light and "
            "background; the question is whether the face comes with it."),
    "s45": ("0.45", True,
            "The top of the bracket. The most scene change the route is "
            "allowed to buy before the face is at risk."),
    "s55": ("0.55", False,
            "A PROBE, NOT A CANDIDATE, and it is outside the bracket on "
            "purpose. Three cells inside a range can say which is best and "
            "cannot say where the range ends. If 0.55 still holds his face the "
            "bracket was set too low and round two can afford real scene "
            "change; if 0.55 breaks it, the ceiling is measured once and never "
            "guessed again. It is excluded from the pick by construction."),
}

# BEAT 13'S OWN STAGING, from jerry_canon_0821.WAVE[13], because a plate that
# is not a beat is not worth judging. The identity clause is NOT included: his
# face is the INIT now, and re-describing it in words is precisely the move
# that is closed by rule.
PROMPT = ("a small green goblin sitting in tall grass, hands clasped between "
          "knees, head tipped sideways, resting, detailed cinematic anime, "
          "masterpiece, best quality, very aesthetic")

# THE NEGATIVE CARRIES NO FACE TERM AT ALL, AND THAT IS THE RULE BEING
# FOLLOWED. The canon negative bans large eyes, thick eyebrows, human face,
# wrinkled skin, old man, glowing eyes, orange eyes, third eye -- every one of
# them a word aimed at the face, and the route closure forbids exactly that.
# His face arrives as pixels; a word defending it would be the seventeenth
# round of the thing that failed sixteen times. What is left is medium and
# quality, which are not claims about him.
NEGATIVE = ("lowres, worst quality, low quality, text, watermark, "
            "photorealism, 3d render, blurry, 2boys, multiple heads")

BAR = """THE ONLY BAR IS HIS IMAGE, AT 1:1, SIDE BY SIDE.
`taste/refs/goblin-canon-founder-0821.png` and this frame, same scale, nothing
else consulted. Not tile B, not any previous round, not a metric.

  E1 THE EYE. Narrow almond, off-white field, a TINY dark pupil, heavy upper
     lid. This is the axis four vetoes were spent on. A large round iris of any
     colour is a FAIL, and it is the failure every one of the sixteen prompt-
     side rounds produced.
  E2 THE SKULL AND EARS. Broad low dome; smallish pointed ears sitting NEAR
     HORIZONTAL, not swept up and back. A tall egg skull with large upswept
     ears is the vetoed design.
  E3 THE FACE IS SMOOTH. No brow furrows, no nasolabial folds, no jowls. He is
     not an adult man.
  E4 PALETTE. Desaturated sage, washed and high-key. Saturated kelly green is
     the vetoed palette.
  E5 COSTUME. The shirt with its placket, dark shorts, dark boots.

AND ONE BAR THAT IS ABOUT THE ROUTE RATHER THAN THE FACE:
  R1 DID ANYTHING HAPPEN? A frame byte-identical in feel to the init is not a
     pass, it is a null -- it means the strength is too low to build a plate
     from and the route needs a higher floor. Report what MOVED: light,
     background, grass, pose, framing.

NOT SCORED, AND NAMED SO IT CANNOT BE READ AS A MISS: THE POSE. He is standing
in the init and beat 13 is seated. At 0.30-0.45 the init owns the composition.
A standing figure here is the expected result and round two is where the
skeleton arrives."""

PREDICTED = """FIRST, AND IT IS THE ONE THAT WOULD KILL THE ROUTE: R1, THE NULL.
At 0.30 over a full frame the pass runs 12 of 40 steps from a latent that still
holds his entire drawing, and it may simply hand back his image. That is not a
face failure, it is a route failure of a different shape -- it would mean
img2img-from-canon cannot produce a DIFFERENT PICTURE of him, only a re-render
of the one we have, and the durable fix (a LoRA trained on his pixels) becomes
the only path rather than the second step. The 0.55 probe exists to bound this.
SECOND: THE FACE BREAKS SOMEWHERE IN THE BRACKET. Expected, and it is what a
bracket is for. The useful outcome is the crossing point -- the highest
strength at which E1-E5 still hold -- because that number is the route's
operating parameter for every beat afterwards.
THIRD, AND IT IS NOT A FAILURE: THE POSE DOES NOT MOVE. Named in the bar above
as not scored. Round two is ControlNet at the winning strength.
WHAT WOULD SURPRISE ME: the face surviving at 0.55 with real scene change. That
would mean the init carries identity far more strongly than the sixteen rounds
of embedding work ever managed, which is the whole hypothesis, and it would
make the goblin dataset cheap to build."""


def main() -> int:
    write = "--write" in sys.argv
    mp = os.path.join(REPO, MASK_DIR, MASK)
    if not os.path.isfile(mp):
        print("!! %s/%s missing" % (MASK_DIR, MASK))
        return 1
    mask_sha = hashlib.sha256(open(mp, "rb").read()).hexdigest()
    canon_sha = hashlib.sha256(
        open(os.path.join(REPO, CANON), "rb").read()).hexdigest()
    if canon_sha != CANON_SHA:
        print("!! the canon image hashes %s, spec says %s" % (canon_sha, CANON_SHA))
        return 1

    for cell in sorted(CELLS):
        strength, candidate, cell_why = CELLS[cell]
        new_id = "ep2-b13-i2icanon-%s-0822" % cell
        dirtok = "b13i2icanon-%s-0822" % cell
        init_name = "goblin-canon-founder-0821.png"

        np_ = assert_under_clip77("%s prompt" % new_id, PROMPT)
        nn_ = assert_under_clip77("%s negative" % new_id, NEGATIVE)

        fetch = '''#!/usr/bin/env python3
"""Fetch THE CANON IMAGE ITSELF as this job's init, and the full-frame mask.
The init is taste/refs/goblin-canon-founder-0821.png at commit b93a70da -- the
picture the founder selected with "dude, this is how the goblin should look".
It is fetched by sha256 and refused on any mismatch, which matters more here
than it has anywhere else in this tree: the init IS the canon."""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\%s"
BASE = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
UA = {"User-Agent": "banyan-city-i2icanon/1.0 (albert.numbro@gmail.com)"}
WANT = {
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
''' % (dirtok, init_name, CANON, CANON_SHA, MASK, "%s/%s" % (MASK_DIR, MASK),
       mask_sha)

        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "the goblin img2img lane, 2026-08-22",
                "consumer": (
                    "THE FOUNDER, AND HE IS AWAKE AND WAITING FOR IT. This is "
                    "round one cell %s of the route that replaces the one he "
                    "vetoed four times. If the bracket holds his face, this "
                    "becomes the plate route for every goblin beat and the "
                    "seed of a goblin LoRA trained on his own pixels. If it "
                    "does not, sixteen rounds of prompt-side work and this "
                    "one are all closed and the next move is his." % cell),
                "success": (
                    "ONE 832x1216 png at strength %s in which E1-E5 hold "
                    "against his image at 1:1 AND something visibly moved "
                    "(R1). Both halves are required: a frame that is his "
                    "image again is a null, not a pass." % strength),
                "why": (
                    "SAPLING-STYLE 0.30 PASS, POINTED AT A FACE. %s\n\n"
                    "THE ROUTE IS CLOSED BEHIND THIS ONE. The founder vetoed "
                    "all four eye rounds including r11a -- 'these are not my "
                    "goblin' -- the fourth veto on an axis that has now cost "
                    "roughly sixteen rounds, every one of them moving a word "
                    "or an IP-Adapter scale. canon.yaml "
                    "`route_closure_2026_08_22` forbids any further face tag, "
                    "adapter scale or reference re-crop. His pixels enter as "
                    "PIXELS or not at all." % cell_why),
            },
            overrides={
                "key:node": "002b-first-citizen",
                "key:beat": BEAT,
                "key:priority": 2,
                "key:est_minutes": 3,
                "key:sample": True,
                "payload:prompt.txt": PROMPT,
                "payload:negative.txt": NEGATIVE,
                "payload:fetch_init.py": fetch,
                "argv:--seed": str(SEED),
                "argv:--strength": strength,
                "argv:--init-sha256": CANON_SHA,
                # PAD-CROP OFF. padding_mask_crop zooms a SMALL mask to model
                # resolution; with a full-frame mask there is nothing to zoom
                # and leaving it at 64 would crop-and-rescale the whole frame
                # for no reason.
                "argv:--pad-crop": "0",
                "argv:--note": (
                    "IMG2IMG FROM THE CANON IMAGE, cell %s, strength %s. The "
                    "mask is FULL FRAME (all white), which turns the SDXL "
                    "inpaint pipeline on base weights into plain img2img: the "
                    "whole frame is denoised from a latent that still carries "
                    "the founder's own picture. THERE IS NOTHING TO CHECK ON "
                    "THE DRY PNG's geometry -- the mask is the frame by "
                    "construction. The dry step is kept anyway because it "
                    "verifies the init's sha256 before a model loads, and the "
                    "init is the canon." % (cell, strength)),
            },
            retoken=[(PARENT_MASKTOK, MASK[:-4]),
                     (PARENT_INITTOK, init_name[:-4]),
                     (PARENT_DIRTOK, dirtok),
                     (PARENT_OUTTOK, "b13-i2icanon-%s" % cell)],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "is_candidate": candidate,
                "the_one_variable": (
                    "THE STRENGTH, %s. Across the four cells the init, the "
                    "mask, the prompt, the negative, the seed (%d) and every "
                    "sampler number are identical, so a difference between "
                    "cells is the strength and nothing else." % (strength, SEED)),
                "the_rung_this_is_one_variable_from": (
                    "NOTHING IN THE CANON WAVE. This is not a rung on that "
                    "ladder, it is a different route: that ladder conditioned "
                    "on his image through an ENCODER and this conditions on it "
                    "as PIXELS. Comparing a cell here to w4 or w7a compares two "
                    "methods, not two settings."),
                "route_closure": (
                    "pipeline/canon.yaml `route_closure_2026_08_22` and the "
                    "2026-08-22 entry in pipeline/work-ladder-0819.md. No face "
                    "tag, no IP-Adapter scale, no reference re-crop -- this "
                    "spec's negative carries no face term at all, which is the "
                    "closure being obeyed rather than described."),
                "clip77_measured_not_estimated": (
                    "positive %d of 77, negative %d of 77, on animagine's own "
                    "vocab." % (np_, nn_)),
                "round_2_lever": (
                    "NAMED BEFORE THE RENDER, in order:\n"
                    "  1. THE FACE HOLDS AND NOTHING MOVED (R1 null) -> raise "
                    "the strength above the winning cell, not lower it, and "
                    "the 0.55 probe already says whether that is affordable.\n"
                    "  2. THE FACE HOLDS AND THE POSE IS WRONG -> ControlNet "
                    "at the winning strength, skeleton from jerry_canon_0821. "
                    "This is the expected round two.\n"
                    "  3. THE FACE BREAKS AT EVERY STRENGTH THAT MOVES "
                    "ANYTHING -> the route cannot make new pictures of him and "
                    "the only remaining path is a LoRA trained on his pixels "
                    "plus augmentation, which is the durable fix anyway.\n"
                    "One at a time, and at most two rounds before this goes "
                    "back to the founder either way."),
                "post_ship_patch": (
                    "review/ep2-ship-0821 IS NOT TOUCHED. A frame here is a "
                    "sample of a ROUTE, not a plate candidate for any beat."),
            },
            by="pipeline/derive_goblin_i2i_0822.py")

        joined = repr({k: v for k, v in child.items() if k != "derivation"})
        for tok in (PARENT_DIRTOK, PARENT_OUTTOK, PARENT_INITTOK, PARENT_MASKTOK):
            if tok in joined:
                raise SystemExit("!! %s still names the parent's %r" % (new_id, tok))
        names = [st["name"] for st in child["steps"]]
        if names.count("fetch") != 1:
            raise SystemExit("!! %s has %d fetch steps" % (new_id, names.count("fetch")))
        pay = child["payload"][r"C:\banyan-farm\%s\prompt.txt" % dirtok]
        neg = child["payload"][r"C:\banyan-farm\%s\negative.txt" % dirtok]
        # THE CLOSURE, ASSERTED IN CODE. A face term on either side of the
        # prompt is the thing sixteen rounds were spent on and the thing
        # route_closure_2026_08_22 forbids. A guard is the only reason a
        # copy-paste from the canon deriver cannot bring one back.
        for dead in ("eyes", "eyebrow", "pupil", "jitome", "eyebags", "ears",
                     "bald", "skin", "wrinkled", "old man", "face"):
            if dead in pay.lower():
                raise SystemExit("!! %s: face term %r is in the POSITIVE -- the "
                                 "route closure forbids it" % (new_id, dead))
            if dead in neg.lower():
                raise SystemExit("!! %s: face term %r is in the NEGATIVE -- the "
                                 "route closure forbids it" % (new_id, dead))
        argv = [t for s in child["steps"] for t in s.get("argv", [])]
        for flag, wantv in (("--strength", strength), ("--pad-crop", "0"),
                            ("--init-sha256", CANON_SHA), ("--seed", str(SEED))):
            got = argv[argv.index(flag) + 1]
            if got != wantv:
                raise SystemExit("!! %s: %s is %r want %r"
                                 % (new_id, flag, got, wantv))

        out = "pipeline/jobs/%s.yaml" % new_id
        if write:
            derive_spec.write(child, out)
            print("wrote %s   strength=%s  candidate=%s" % (out, strength, candidate))
        else:
            print("%-32s strength=%-5s candidate=%-5s clip77 %d/%d"
                  % (new_id, strength, candidate, np_, nn_))
    if not write:
        print("\n-- dry run, %d cell(s). re-run with --write." % len(CELLS))
        print("   prompt : %s" % PROMPT)
        print("   negative: %s" % NEGATIVE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
