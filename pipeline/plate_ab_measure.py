#!/usr/bin/env python3
"""Is frame 0 of a clip a cover-crop of its still, or a stretch of it?

THE TEST, and why it is a measurement rather than a look. Every canon still is
832x1216 (aspect 0.6842); every clip renders at 704x1280 (0.5500). A renderer
that resizes without regard to aspect makes the picture 1.2440x too tall, and
that defect "raises nothing and looks like a resize that does not"
(plate_prep.py:8-16) -- on a single frame, at a glance, a 24% stretch of a plant
just looks like a slightly different plant.

So the frame is compared against two reconstructions built from its OWN approved
still: a naive stretch, and the cover-centre crop that plate_prep and render_t3
both produce. Mean absolute pixel difference; lower is what the clip actually is.
The two numbers are reported together and neither means anything alone -- the
finding is which of them is small, and the margin between them.

This is NOT a quality metric and it ranks nothing. The flow metric is disqualified
as a selection criterion on this series (131e433 scored highest on the beat where
the plant fell over), and this number is deliberately a different kind of thing:
it answers a closed geometric question with a known right answer, and a clip that
passes it can still be a bad clip.

    python3 pipeline/plate_ab_measure.py --still <still.png> <clip.mp4> [clip.mp4 ...]

Needs ffmpeg on PATH and PIL. Frame 0 is extracted to a PNG beside the clip.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def frame0(mp4: str, out_dir: str):
    """Extract frame 0 losslessly to PNG and return it as RGB."""
    from PIL import Image

    out = os.path.join(out_dir, os.path.basename(mp4) + ".f0.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4,
                    "-frames:v", "1", out], check=True)
    return Image.open(out).convert("RGB")


def mad(a, b) -> float:
    """Mean absolute difference over every channel of every pixel, 0-255.

    Whole-frame on purpose. A stretch is a global geometric error, so it shows up
    everywhere at once; averaging over the frame is what makes the two numbers
    separate by a factor of six rather than by noise.
    """
    if a.size != b.size:
        raise SystemExit("!! size mismatch %s vs %s" % (a.size, b.size))
    pa, pb = a.tobytes(), b.tobytes()
    return sum(abs(x - y) for x, y in zip(pa, pb)) / len(pa)


def main(argv=None) -> int:
    from PIL import Image
    from plate_prep import fit_cover

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--still", required=True, help="the approved still the clips came from")
    ap.add_argument("--size", default="704x1280")
    ap.add_argument("--plate", help="optional: a prepared plate, checked against "
                                    "our own cover-crop (0.0 = same policy)")
    args = ap.parse_args(argv)

    W, H = (int(v) for v in args.size.lower().split("x"))
    with Image.open(args.still) as raw:
        still = raw.convert("RGB")
    sw, sh = still.size
    print("still %dx%d aspect %.4f   target %dx%d aspect %.4f   ratio %.4f"
          % (sw, sh, sw / sh, W, H, W / H, (sw / sh) / (W / H)))

    stretch = still.resize((W, H), Image.LANCZOS)
    crop, info = fit_cover(still, W, H)
    print("crop policy: %s" % info["crop_note"])

    if args.plate:
        p = Image.open(args.plate).convert("RGB")
        print("plate vs recomputed cover-crop: MAD %.4f" % mad(p, crop))

    print("\n%-46s %10s %10s   %s" % ("clip", "vs STRETCH", "vs CROP", "frame 0 is"))
    rc = 0
    for clip in args.clips:
        f0 = frame0(clip, os.path.dirname(os.path.abspath(clip)))
        if f0.size != (W, H):
            print("%-46s frame0 is %dx%d, not %dx%d" % (os.path.basename(clip),
                                                        f0.size[0], f0.size[1], W, H))
            rc = 1
            continue
        s, c = mad(f0, stretch), mad(f0, crop)
        print("%-46s %10.2f %10.2f   %s" % (os.path.basename(clip), s, c,
                                            "COVER-CROP" if c < s else "STRETCH"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
