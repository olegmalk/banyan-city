#!/usr/bin/env python3
r"""The two flat plates that turn `inpaint_fruit.py` into txt2img-with-ControlNet.

WHY THESE TWO FILES EXIST AT ALL.
`registry.yaml`'s bnyjerry v2 entry closed B2 -- pose adoption, the only bar
whose answer changes what the show can do -- as VOID rather than failed. Two
controls said why: with NO LoRA loaded, on BOTH of xinsir's openpose blobs,
`controlnet_plate.py`'s txt2img path drew an unrelated standing figure. The net
was never driving in that path. The SAME net measurably drives through
`inpaint_fruit.py` (15.05 mean abs, goblin i2i route round two), and the entry
named the cheapest fix rather than a debugging expedition:

    inpaint_fruit.py + an ALL-WHITE MASK at STRENGTH 1.0 *is*
    txt2img-with-ControlNet, on the one code path where the pose net is proven
    to act.

An all-white mask means every pixel is redrawn; strength 1.0 means every
timestep runs, so the init is fully noised before the first step and contributes
nothing. The init is therefore a REQUIRED ARGUMENT WITH NO INFLUENCE -- the
driver refuses without one and pins its sha256 -- and a flat mid-grey is the
honest thing to hand it: any picture there would look like a source it is not.

WHY THEY ARE COMMITTED AND FETCHED BY SHA RATHER THAN GENERATED ON THE BOX.
The driver takes `--init-sha256` and refuses on mismatch, so the hash has to be
known at ENQUEUE time; a plate generated on the card at run time has no hash
until after the argv that pins it was written. Every asset this tree sends to
the card is pinned and refused on mismatch, and these are no exception.

  python3 pipeline/author_jerry_poseproof_0822.py            # dry
  python3 pipeline/author_jerry_poseproof_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "farm-out", "jerry-poseproof-assets-0822")

# THE SIZE IS NOT A CHOICE. Every jerry skeleton in
# farm-out/jerry-canon-assets-0821/ is 832x1216, `inpaint_fruit.py` hard-refuses
# rc 13 on a hint that is not the init's exact pixel size, and 832x1216 is the
# size all four filed bar grids were rendered at.
W, H = 832, 1216

# A NEUTRAL GREY, AND THE VALUE IS ARBITRARY BECAUSE THE MECHANISM MAKES IT SO.
# At strength 1.0 the scheduler noises the init to the terminal sigma before
# step one. 128 is stated rather than chosen: a mid-grey reads at a glance as
# "no picture was here", which is what the sidecar's init line should mean.
GREY = 128

PLATES = {
    "jerry-poseproof-init-0822.png": ("RGB", (GREY, GREY, GREY)),
    "jerry-poseproof-maskall-0822.png": ("L", 255),
}


def build() -> dict:
    """name -> (bytes, sha256). Deterministic: PIL writes these byte-for-byte."""
    import io
    out = {}
    for name, (mode, colour) in sorted(PLATES.items()):
        buf = io.BytesIO()
        # optimize/compress_level left at PIL's defaults on purpose -- the bytes
        # only have to be STABLE, and a tuned encoder is one more thing that
        # could differ between the machine that hashes and the machine that reads.
        Image.new(mode, (W, H), colour).save(buf, format="PNG")
        raw = buf.getvalue()
        out[name] = (raw, hashlib.sha256(raw).hexdigest())
    return out


def main() -> int:
    write = "--write" in sys.argv
    built = build()
    if write:
        os.makedirs(OUT, exist_ok=True)
    for name, (raw, sha) in sorted(built.items()):
        path = os.path.join(OUT, name)
        if write:
            with open(path, "wb") as fh:
                fh.write(raw)
        print("%s %s  %d bytes  %s"
              % ("wrote " if write else "would", name, len(raw), sha))
    # THE MASK IS ASSERTED, NOT ASSUMED. An "all-white" mask with one grey pixel
    # in it is an inpaint, not a txt2img, and the difference would be invisible
    # in the picture and fatal to the reading.
    import io
    m = Image.open(io.BytesIO(built["jerry-poseproof-maskall-0822.png"][0]))
    hist = m.convert("L").histogram()
    assert hist[255] == W * H and sum(hist[:255]) == 0, \
        "the mask is not every-pixel white, so this is an inpaint and not txt2img"
    print("MASK IS %d/%d WHITE PIXELS -- every pixel is redrawn" % (hist[255], W * H))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
