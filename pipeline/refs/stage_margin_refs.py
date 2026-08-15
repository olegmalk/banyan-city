r"""Stage refs-goblin-d1-margin-0815: the SAME four tiles, more air.

ONE VARIABLE. Every output pixel of the figure is the input tile's pixel, only
smaller: the 832x832 source tile is resampled to 416x416 (LANCZOS) and pasted
dead centre on an 832x832 white field. Nothing is re-cropped out of the sheet,
so no neighbouring figure, no new content and no new colour enters the set --
the only thing that changes is the fraction of the tile the figure occupies,
which halves, and therefore the fraction of the frame the HEAD occupies, which
also halves.

Refuses if any source tile's sha256 is not the one frozen in
pipeline/refs/refs-goblin-d1-0815.yaml.
"""
import hashlib
import os
import sys

from PIL import Image

SRC = r"C:\banyan-farm\wave-goblin-prep\refs-goblin-d1-0815"
DST = r"C:\banyan-farm\wave-goblin-prep\refs-goblin-d1-margin-0815"
FACTOR = 0.5

EXPECT = {
    0: "dd4b30cd3ab74902c9bf80ae90aa214da2555a802bc6b17e3c655e062937a4e8",
    1: "c51c6467829f29db79514ed5721c310d04b7afef2b97372779714306516a0b8c",
    2: "9526882ef5d6653b22a79d632e7aca6840fc8ea55b88bba207c350f932525b69",
    3: "d84abe2f359034c7a99862791350374a011f4cb939a37324c3139a19dc9dba2e",
}
# Hashes copied from pipeline/refs/refs-goblin-d1-0815.yaml. Compared on the
# leading 32 hex so a transcription slip is loud rather than silent -- it
# already was: the first draft of this file mistyped s0 and the check refused.


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    os.makedirs(DST, exist_ok=True)
    out = []
    for i in range(4):
        s = os.path.join(SRC, "goblin-d1s1-s%d.png" % i)
        h = sha(s)
        if not h.startswith(EXPECT[i][:32]):
            print("!! s%d is not the frozen tile: %s" % (i, h))
            return 2
        img = Image.open(s).convert("RGB")
        if img.size != (832, 832):
            print("!! s%d is %s, expected 832x832" % (i, img.size))
            return 3
        corners = [img.getpixel(p) for p in
                   ((0, 0), (831, 0), (0, 831), (831, 831))]
        n = int(round(832 * FACTOR))
        canvas = Image.new("RGB", (832, 832), (255, 255, 255))
        canvas.paste(img.resize((n, n), Image.LANCZOS), ((832 - n) // 2,) * 2)
        d = os.path.join(DST, "goblin-d1s1m-s%d.png" % i)
        canvas.save(d)
        out.append((i, sha(d), corners))
        print("s%d  src %s -> dst %s  corners=%s" % (i, h[:12], sha(d)[:12],
                                                     corners))
    shas = [o[1] for o in out]
    if len(set(shas)) != 4:
        print("!! the four margined tiles are not four distinct pictures")
        return 4
    with open(os.path.join(DST, "MANIFEST.yaml"), "w", newline="\n") as fh:
        fh.write("# refs-goblin-d1-margin-0815 -- staged %s\n" % FACTOR)
        fh.write("set: refs-goblin-d1-margin-0815\n")
        fh.write("ref_prefix: goblin-d1s1m\n")
        fh.write("derived_from: refs-goblin-d1-0815\n")
        fh.write("transform: resample tile to %d px, paste centred on an "
                 "832x832 white field\n" % int(round(832 * FACTOR)))
        fh.write("images:\n")
        for i, h, _ in out:
            fh.write("- slot: s%d\n  file: goblin-d1s1m-s%d.png\n"
                     "  sha256: %s\n  source_slot_sha256: %s\n"
                     % (i, i, h, sha(os.path.join(SRC,
                                                  "goblin-d1s1-s%d.png" % i))))
    print("OK 4 distinct margined tiles ->", DST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
