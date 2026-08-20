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

The generator body is kept verbatim below as it was run.
"""
