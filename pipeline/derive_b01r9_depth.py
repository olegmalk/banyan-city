"""Beat 01 round 9, stage 0: derive the depth conditioning map from the plate.

The map is COMMITTED as an artifact (B01-R9-PLAN.md section 4); this script is
how it was made and how to check it, not a render-time step. Regenerating at
render time would make the round depend on a model download staying
byte-stable, which is the weaker design.

The map is a pure function of the approved still under pinned weights:
DPTImageProcessor defaults, torch.inference_mode, fp32 on CPU, min-max
normalise, replicate to 3 channels. It carries strictly less than the still —
one channel of geometry, colour discarded — so it cannot introduce unapproved
content. Both the source sha256 and the produced sha256 are asserted.

CPU rather than CUDA deliberately: the map has to be reproducible on a box
whose card is busy, and fp32 on CPU removes autocast from the chain. MiDaS/DPT
predicts INVERSE depth, so near comes out bright; see the polarity gate.

    python3 pipeline/derive_b01r9_depth.py <plate.png> <out.png> [--check]

--check derives to a temp file and compares against <out.png> instead of
writing, so the committed artifact can be re-verified without replacing it.
"""
import argparse
import hashlib
import os
import sys
import tempfile

PLATE_SHA256 = "f60c1404f88d45720ca295dfc753e9eaabb815446710bcfffb3c7a07b7277f54"
MAP_SHA256 = "fda4bf6c8838c2da770ce79dd36c885f3c1699755fbb7ce4b0581fd1c32adc28"
ESTIMATOR = "Intel/dpt-hybrid-midas"
ESTIMATOR_REVISION = "11eaf7a1cf4bd70740697dbc216f98980c0aeb03"
RENDER_W, RENDER_H = 832, 1216


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def derive(plate_path, out_path):
    import numpy as np
    import torch
    from PIL import Image
    from transformers import DPTForDepthEstimation, DPTImageProcessor

    estimator = DPTForDepthEstimation.from_pretrained(
        ESTIMATOR, revision=ESTIMATOR_REVISION).eval()
    processor = DPTImageProcessor.from_pretrained(
        ESTIMATOR, revision=ESTIMATOR_REVISION)

    plate = Image.open(plate_path).convert("RGB")
    inputs = processor(images=plate, return_tensors="pt")
    with torch.inference_mode():
        predicted = estimator(**inputs).predicted_depth

    depth = torch.nn.functional.interpolate(
        predicted.unsqueeze(1), size=(RENDER_H, RENDER_W),
        mode="bicubic", align_corners=False)
    dmin = torch.amin(depth, dim=[1, 2, 3], keepdim=True)
    dmax = torch.amax(depth, dim=[1, 2, 3], keepdim=True)
    depth = (depth - dmin) / (dmax - dmin)
    arr = torch.cat([depth] * 3, dim=1).permute(0, 2, 3, 1).cpu().numpy()[0]
    Image.fromarray((arr * 255.0).clip(0, 255).astype("uint8")).save(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plate")
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true",
                    help="derive to a temp file and compare, do not overwrite")
    args = ap.parse_args()

    got = sha256(args.plate)
    if got != PLATE_SHA256:
        sys.exit("plate sha256 %s != approved b15-r3-s1 %s — G1 refuses to start"
                 % (got, PLATE_SHA256))
    print("plate sha256 OK %s" % got)

    if args.check:
        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            derive(args.plate, tmp)
            fresh = sha256(tmp)
        finally:
            os.unlink(tmp)
        print("re-derived sha256 %s" % fresh)
        print("committed  sha256 %s" % sha256(args.out))
        if fresh != sha256(args.out):
            sys.exit("MISMATCH — the committed map is not reproducible here")
        print("MATCH — committed map reproduces")
        return

    derive(args.plate, args.out)
    out = sha256(args.out)
    print("map sha256 %s" % out)
    if out != MAP_SHA256:
        print("WARNING: differs from the recorded map sha256 %s" % MAP_SHA256)


if __name__ == "__main__":
    main()
