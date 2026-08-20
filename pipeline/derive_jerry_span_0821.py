#!/usr/bin/env python3
r"""GIVE THE NET THE SPAN AND LET THE FOLD COME FROM THE WORDING.

`sit`, `kneel` and `crouch` all came back as SMALL FIGURES with oversized heads
while the head keypoints were byte-identical to the standing rung's -- the net
reads a short skeleton as a small person. Before that becomes a written limit it
gets the cheap test, three rungs, one variable each.

  s1  the STANDING skeleton (span 0.965) with SEATED wording. The purest form of
      the hypothesis. Also the most informative failure: Sec 13 measured this
      net binding composition to the pixel, so a standing skeleton SHOULD draw a
      standing figure and the wording should lose. If it does not, the net is a
      suggestion rather than a constraint on this checkpoint, and that is worth
      more than the pose.
  s2  THE TILE'S ACTUAL STANCE. The stance authored as `sit` was wrong: the tile
      is not folded on the ground, he is SITTING ON SOMETHING WITH HIS FEET FLAT
      -- soles at y=915, crown at y=292 in adult-b19-0819.jpg, which is 0.77 of
      his standing height. `seatspan` authors that: hips at knee height, knees
      forward and level, ankles on the same foot line every rung since n1 has
      used. Span 0.486 -> 0.689.
  s3  s2 WITH THE AUTHORED HEAD PRE-SHRUNK to head_frac 0.145, putting authored
      heads-over-span at 4.72 instead of 3.63. The mechanistic compensation: the
      measured relation is that DRAWN heads-over-span falls with span (5.07 at
      span 0.965, 3.06 at 0.486), which reads as the net sizing the head to the
      skeleton's extent. If that is the mechanism, s3 lands and s2 does not.

IF ALL THREE FAIL the stop gets written: openpose cannot give a folded pose at
this character's proportion, the LoRA's pose gate is not dischargeable by this
instrument, and the route is IP-Adapter off the tile's own seated frame.

The generator is below. NOTE: the three specs on the card were emitted by this
same code run inline before this file existed; re-running it rewrites them
byte-identically except for the four FRESH sentences, which derive_spec
refuses to inherit and which are abbreviated here. The specs on disk carry
the full ones.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402
import derive_jerry_skel_0820 as skel  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMIT = "a34331f74b217004c8e3535f03c5d6f72173d90f"
SEAT_SHA = {
    "jerry-skel-h19seat-0820":
        "adaf7f1ed44b9d6ed990a40dbbf6396c19c08f2ade83723cd0aac976fe0210cb",
    "jerry-skel-h145seat-0820":
        "a8856a2d539e08dd31f175a85cbec0541701e1379f1dfa2baffa5829e2589983",
}
skel.HINT_SHA.update(SEAT_SHA)
SEATED = "sitting, hands clasped between knees, in tall grass, full body"

RUNGS = [
    ("s1", "jerry-skel-h19-0820", SEATED,
     "THE STANDING SKELETON WITH SEATED WORDING. The span is n1's -- 0.965 of "
     "stature, the span that works -- and the fold is asked for in words only."),
    ("s2", "jerry-skel-h19seat-0820", SEATED,
     "THE TILE'S ACTUAL STANCE at 0.689 span, head_frac unchanged at 0.190."),
    ("s3", "jerry-skel-h145seat-0820", SEATED,
     "s2's stance with the AUTHORED HEAD PRE-SHRUNK to head_frac 0.145, which "
     "puts authored heads-over-span at 4.72 instead of 3.63."),
]

BAR = """T8 IS THE WHOLE QUESTION AND IT IS READ AGAINST THE TILE, NOT AGAINST A
STANDING FIGURE. adult-b19-0819.jpg is 4.0 heads crown-to-sole SEATED. PASS is
3.6 or better crown-to-sole with lean limbs; `sit` measured 3.06.
T9 THE POSE IS SEATED. s1 can fail this and s2/s3 cannot.
REGRESSION: T1 blank eyes, T2 no human nose, T3 no age modelling."""


def main():
    for suffix, hint, pose_words, variable in RUNGS:
        new_id = "ep2-jerry-span-%s-0820" % suffix
        job_dir = "jerryspan-%s-0820" % suffix
        child = derive_spec.derive(
            src=skel.PARENT, new_id=new_id,
            fresh={"owner": "goblin reference-route lane, 2026-08-21",
                   "why": "RUNG %s: %s" % (suffix, variable),
                   "consumer": "THE JERRY LoRA'S POSE GATE.",
                   "success": "ONE 832x1216 png at seed %d on %s.png."
                              % (skel.SEED, hint)},
            overrides={
                "seed": skel.SEED, "argv:--scale": "1.0",
                "argv:--control-sha256": skel.HINT_SHA[hint],
                "argv:--repo-commit": COMMIT,
                "payload:prompt.txt": skel.prompt_for(pose_words),
                "payload:negative.txt": skel.NEG,
                "key:beat": 2, "key:priority": 27, "key:est_minutes": 3},
            retoken=[(skel.PARENT_DIR_TOKEN, job_dir),
                     (skel.PARENT_HINT_TOKEN, hint)],
            extra={"bar": BAR, "the_one_variable": variable},
            by="pipeline/derive_jerry_span_0821.py")
        child["steps"] = [{
            "name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c",
                     skel.stage_step(job_dir, hint)],
        }] + list(child["steps"])
        out = "pipeline/jobs/%s.yaml" % new_id
        derive_spec.write(child, out)
        derive_fetch_guard.assert_fetch_urls_resolve(
            os.path.join(REPO, out),
            must_hold=("controlnet_plate.py", hint + ".png"))
        print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
