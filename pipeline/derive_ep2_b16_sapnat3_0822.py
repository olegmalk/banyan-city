#!/usr/bin/env python3
r"""BEAT 16's NATURALIZE, ON A PLANT THAT IS GREEN BECAUSE THE SAMPLER WAS FIXED.

    python3 pipeline/derive_ep2_b16_sapnat3_0822.py [--write]

WHY BEAT 16 HAD NO PLATE THIS MORNING, and it was not the plate. The morning
compositor lane drew the canon sapling into `ep2-b16-canon-w4-0821` twice,
refused both by eye, and recorded the cause:

    "its foreground is a SHALLOW-FOCUS BLUR WITH BLOWN HIGHLIGHTS, and its
     green-dominant p88 is (239,255,230). foliage_palette takes the highlight
     from that percentile on purpose, so the crescent comes back near-white and
     the plant reads as a ghost over his chest. The anti-decal law is doing its
     job and the answer is a different PLATE, not a different palette."

THE PERCENTILE WAS RIGHT AND THE SET IT WAS TAKEN OVER WAS WRONG.
`foliage_palette` selected on `G > R+6 and G > B+6`, which is a test of which
channel is LARGEST and not of whether the pixel has any colour in it. A blown
highlight at (241,255,232) passes it and is white. On this exact plate's lower
third that was 44% of the sample and the top 44% by luminance, so it owned the
p88 outright:

    | selection                     |      n | p88 highlight |
    |-------------------------------|--------|---------------|
    | as shipped                    | 92,974 | (241,255,232) |
    | + chroma >= 0.15              | 54,622 | (147,168,126) |

With the floor in, the SAME PLATE cuts a green plant. Both arms are committed:
`b16-satfloor0-white-control-0822.png` is the ghost, `b16-sapnat3-in-0822.png`
is the fix, one flag apart.

> A DOMINANCE TEST IS NOT A COLOUR TEST. Wherever a percentile is read over
> "pixels whose channel X is largest", the achromatic end of the plate is in the
> set and sits at one extreme of the luminance order -- which is exactly where
> the percentiles that matter are taken.

AND A FOUR-CELL PLATE LADDER WAS FIRED THIS MORNING FOR THE WRONG CAUSE, which
is the other half of the lesson and is worth more than the four GPU minutes.
`ep2-b16-canon-w5{z,a,b,c}-0821` killed the depth of field in the negative and
added the sapling-field lane's distance clause. Both are NULLS on the
foreground -- green p88 240 / 252 / 247 against w4's 241, and no hills appeared
-- and the strip that bought the CLIP-77 headroom BROKE THE EYE on all four
cells. w4 stands, and it never needed replacing.

WHERE THE PLANT IS PUT, and it is the lane's other named route taken as far as
it goes: root 416,1200, height 780, leaf-frac 0.38 -- low, big, stem running up
through the frame with the two blades at his chin. Beat 16's staging is *"Close
on the sapling's leaf; the scavenger sits blurred behind it"*, so the plant
belongs in front of him and his eyes must stay clear; this placement is the
largest the C3 whole-plant-in-frame check allows on this plate.

WHAT IS NOT FIXED BY THIS, stated so nobody reads a pass here as beat 16 being
done: THE W4 PLATE'S FIGURE FILLS THE FRAME TOP TO BOTTOM, so there is no near
foreground for a plant to be in -- it can only OVERLAP him. The relation beat 16
wants (plant is the subject, he is depth) was staged correctly once, by
`ep2-b16-sapcomp-r2-0820` on the b15 mac plate, whose only defect is that it
predates the founder's 08-21 goblin. Getting both at once is a GEOMETRY
question -- the skeleton's span and head_frac decide how much of the frame the
figure takes, and no word in the positive can move the camera back while
ControlNet is at 1.0 on a full-span skeleton. That is filed, not solved.

WHAT IS HELD FROM THE PARENT: seed 20260820, strength 0.30, 40 steps, cfg 7.5,
pad-crop 64, blur 8, the whole inpaint_fruit.py payload, the env block, the
needs, the dry-run mask gate and the no-glob publish. The prompt's only change
is the goblin's posture word, because beat 03 crouches and beat 16 sits.

$0 to derive. ~4 GPU minutes.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_fetch_guard                                     # noqa: E402
import derive_spec                                            # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77     # noqa: E402
import derive_ep2_sapnat_0821 as P                            # noqa: E402

PARENT = "pipeline/jobs/ep2-b03-sapnat-0821.yaml"
NEW_ID = "ep2-b16-sapnat3-0822"
PUBDIR = "farm-out/ep2-b16-sapnat3-0822"
INIT = "b16-sapnat3-in-0822.png"
MASK = "b16-sapnat3-in-mask-0822.png"
PROMPT = P.prompt_for("sitting in tall grass")

FETCH = '''#!/usr/bin/env python3
"""Fetch beat 16's w4-plate composite and its mask, refusing on any sha
mismatch. Both files are on origin/main, so these sha256s are verifiable
against the repo by anyone who clones it. They were made on a Mac, so they are
NOT on the box's courier worktree -- the courier only ever contains what the
box produced."""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\b16sapnat3-0822"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "farm-out/ep2-b16-sapnat3-0822/")
UA = {{"User-Agent": "banyan-city-b16-sapnat/1.0 (albert.numbro@gmail.com)"}}
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

BAR = """JUDGED BY EYE AT 1:1. THE QUESTION IS WHETHER THE PLANT IS PART OF THE
PICTURE, and the beat is NOT finished by a pass here.

  Q1  THE PLANT IS GREEN AND IT IS THE PLATE'S GREEN. Not white, not a ghost.
      `b16-satfloor0-white-control-0822.png` in the same directory is the
      matched control cut from the same command line with the chroma floor at
      0.0, and it is the ghost the compositor lane refused twice. If the pass
      brings the near-white crescent BACK, the palette fix is not the whole
      story and the plate does have to change.
  Q2  IT IS DRAWN, NOT PASTED -- cel shading and the plate's ink weight, the
      compositor's flat fill and hard cut edge gone.
  Q3  IT HAS NOT MOVED. Root, height and leaf tips within a few px of where the
      compositor put them. 0.30 finishes a structure; a relocated plant means
      the strength was wrong.
  Q4  EXACTLY TWO AVERAGE LEAVES ON ONE STEM. A third leaf, a branch or a lance
      is a FAIL however well drawn -- canon `sapling-two-leaves` plus
      `sapling-cotyledon-shape`.
  Q5  HE SURVIVES UNCHANGED AND HIS EYES ARE CLEAR. The mask is 9.5% of the
      frame and local; anything outside it that moved means the pad-crop
      reached past the geometry. The blades sit at his chin ON PURPOSE (he is
      meant to be behind the leaf) but a leaf across an EYE is a fail.
  Q6  THE INK IS NOT PURE BLACK ON THE EYE. `_character_ink` measured (3,1,8)
      on this plate, which is nearly true black, and the tool's own rule is
      that true black reads as pasted in this dialect. It passed the check
      because the plate really is inked that dark; it is scored anyway because
      it is the one number in this cut that is at an edge.

  AND THE CLAUSE THIS PASS CANNOT ANSWER, named so a pass is not over-read:
  THE RELATION. Beat 16 wants the plant as SUBJECT with him as depth. On this
  plate he fills the frame, so the best available reading is "a plant in front
  of him", not "a close-up of a leaf". That is a plate-geometry question and it
  is open whatever this pass returns."""


def sha256_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build(force=False, write=False):
    init_abs = os.path.join(REPO, PUBDIR, INIT)
    mask_abs = os.path.join(REPO, PUBDIR, MASK)
    for f in (init_abs, mask_abs):
        if not os.path.isfile(f):
            raise SystemExit("!! missing composite input %s" % f)
    init_sha, mask_sha = sha256_of(init_abs), sha256_of(mask_abs)
    assert_under_clip77("b16 prompt", PROMPT)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "early-morning lane, 2026-08-22",
            "consumer": (
                "THE FIRST BEAT-16 PLATE ON THE CORRECTED GOBLIN THAT HAS A "
                "PLANT IN IT. A pass here is a PLATE, not a candidate: the "
                "motion rung is separate and review/ep2-ship-0821 is not "
                "touched. Beat 16 has been a slate since 08-20 and the "
                "founder's card /review/ep2-b16-leaf-0820 is still open with "
                "`licence` still available to him."),
            "success": (
                "ONE 832x1216 png in which the canon two-leaf sapling is drawn "
                "into the frame in the PLATE'S OWN GREEN and has not moved. "
                "Judged by eye at 1:1 against b16-satfloor0-white-control-0822"
                ".png in the same directory, which is the near-white version "
                "this lane's palette fix replaced."),
            "why": (
                "BEAT 16's PLANT CAME BACK WHITE TWICE AND THE CAUSE WAS A "
                "SELECTION BUG, not the plate. foliage_palette read its "
                "highlight percentile over `G > R+6 and G > B+6`, which admits "
                "blown white pixels; on the w4 plate they were 44% of the "
                "sample and the top 44% by luminance. A chroma floor of 0.15 "
                "moves the highlight from (241,255,232) to (147,168,126) off "
                "54,622 pixels of real grass.\n\n"
                "THE FOUR-CELL PLATE LADDER FIRED THIS MORNING TO KILL THE "
                "BLUR IS A NULL and is recorded as one: the depth-of-field "
                "terms and the distance clause moved the foreground green p88 "
                "to 240/252/247 against w4's 241, no hills appeared, and the "
                "negative-token strip that paid for them broke the eye on all "
                "four cells. w4 stands."),
        },
        overrides={
            "argv:--init-sha256": init_sha,
            "payload:prompt.txt": PROMPT,
            "payload:fetch_init.py": FETCH.format(
                init=INIT, mask=MASK, init_sha=init_sha, mask_sha=mask_sha),
            "key:beat": 16,
            "key:priority": 18,
        },
        retoken=[
            ("b03sapnat-0821", "b16sapnat3-0822"),
            ("farm-out/ep2-b03-sapnat-0821/", PUBDIR + "/"),
            ("b03-sapnat-in-mask-0821.png", MASK),
            ("b03-sapnat-in-0821.png", INIT),
            ("b03-sapnat-s", "b16-sapnat3-s"),
            ("b03-sapnat", "b16-sapnat3"),
        ],
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE PLATE AND THE PALETTE FIX TOGETHER, and that is stated "
                "rather than claimed away: this is beat 16's FIRST naturalize, "
                "so there is no parent rung of its own to hold one variable "
                "against. The exact A/B that IS one variable is local and "
                "committed -- b16-satfloor0-white-control-0822.png is the same "
                "command line with --green-sat-floor 0.0."),
            "the_rung_this_is_one_variable_from": (
                "ep2-b03-sapnat-0821 on the RECIPE (every sampler number, the "
                "payload, the seed and the negative are byte-identical); the "
                "prompt differs by one posture word because beat 03 crouches "
                "and beat 16 sits."),
            "init_provenance": (
                "%s/%s, 832x1216, sha256 %s, with its mask %s sha256 %s. Cut "
                "by pipeline/beat16_sapling_composite.py --root 416,1200 "
                "--height 780 --leaf-frac 0.38 from "
                "farm-out/ep2-b16-canon-w4-0821/ep2-b16-canon-w4-0821-ipahead"
                ".png (sha256 6849fcd1a2fe451f7f61a40ffd4fe0be64b3294330fc30aa"
                "9795a82642ceb2e2). Full argv in the geometry json beside the "
                "png. Palette measured off the plate: dark (99,122,105), mid "
                "(120,134,113), light (148,163,126), ink (3,1,8)."
                % (PUBDIR, INIT, init_sha, MASK, mask_sha)),
            "failure_predicted_in_advance": (
                "FIRST, AND IT IS THE ONE THE WHOLE FIX RIDES ON: the pass "
                "brings the near-white crescent back anyway, because the "
                "PLATE's own light in that region is blown and 0.30 pulls the "
                "fill toward it. Then the palette was only half the cause and "
                "the plate does have to change -- and the change is geometry "
                "(a figure that does not fill the frame), not another "
                "negative term, because the four-cell ladder already spent "
                "that route.\n"
                "SECOND: the blades sit at his chin and the pass merges them "
                "into his collar. The collar is inside the mask's dilation, "
                "so this is reachable; a leaf that becomes part of the shirt "
                "fails Q5.\n"
                "THIRD: the ink is (3,1,8), effectively black, against the "
                "tool's own rule that true black reads as pasted. The plate is "
                "genuinely inked that dark so nothing was overridden, but if "
                "the plant reads as a sticker while being the right colour, "
                "the ink is where to look and not the fill."),
            "not_done_on_purpose": (
                "NO MOTION IS FILED BY THIS JOB, and beat 16's relation "
                "problem is NOT claimed as solved. On the w4 plate the figure "
                "fills the frame, so the plant can only overlap him; the "
                "'plant is subject, he is depth' staging that "
                "ep2-b16-sapcomp-r2-0820 got right needs a plate whose "
                "skeleton does not span the picture. That is a geometry rung "
                "and it is named, not fired."),
        },
        by="pipeline/derive_ep2_b16_sapnat3_0822.py")

    out = "pipeline/jobs/%s.yaml" % NEW_ID
    if write:
        derive_spec.write(child, os.path.join(REPO, out), force=force)
        derive_fetch_guard.assert_fetch_urls_resolve(
            os.path.join(REPO, out), must_hold=(INIT, MASK))
        print("wrote %s" % out)
    else:
        print("DRY RUN -- pass --write. id=%s init=%s sha=%s\n  prompt: %s"
              % (NEW_ID, INIT, init_sha[:16], PROMPT))
    return child


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    build(force=a.force, write=a.write)
    return 0


if __name__ == "__main__":
    sys.exit(main())
