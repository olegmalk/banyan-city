#!/usr/bin/env python3
r"""BEAT 05, THE PATROL: two DIFFERENT guards in one frame, from their own canons.

THE ONE-BEAT SAMPLE FOR THE WHOLE EP2 FINISH CHAIN. Composite -> grade ->
naturalize -> motion, on the beat that exercises the most machinery: two figures,
two mattes, two grades, a shared ground and a seam per figure. If the chain
survives motion here, the other fourteen beats are the same chain with fewer
parts. If a naturalize cannot blend a full-character paste, we have spent ONE
beat learning it instead of fifteen.

WHY A COMPOSITE AND NOT A RENDER. Measured today across two plate passes: at
strength 0.30 the prompt buys nothing -- not framing, not ground, not light (four
cells asking four different lights returned mean RGB within two levels of each
other). The route is a pure identity-preserving pass. So every difference between
beats has to come from the compositor, and `composite-init-pattern.md` is the
house doctrine for exactly that: "with a composited init, the thing you want is
not a sample from the model."

WHY THE BEAT IS RESTAGED WIDE -> MEDIUM, and it is a steward call the founder can
veto. The beat is written as a wide two-shot of two guards jogging in. BOTH guard
canons are tight FACE PORTRAITS -- there is no full-body guard art anywhere in
this tree -- so a wide shot cannot be built from them at all. It becomes a medium
two-shot: the show is 9:16 phone-first and its chronic historic fault has been
wide shots with unreadable faces, and "jogging in" reads at medium as entering
frame. Recorded on the beats page as `restaged wide->medium: no full-body guard
art exists`.

THE MATTE IS DELIBERATELY SOFT, AND THAT IS NOT LAZINESS. Doctrine's rule 2 is
"fitted to the object, not to the mask", whose purpose is that texture edge and
object edge coincide -- it exists so bark does not get painted over fingers.
Here the SOURCE surround and the DESTINATION surround are the same material:
defocused meadow grass. A feathered oval that carries a little source grass onto
destination grass has no edge to betray, and the seam the naturalize is asked to
finish is a soft luminance step rather than a cut. A hard matte on hair against
grass would be strictly worse -- it would produce exactly the cliff rule 3 warns
about.

THE PLATE'S OWN LIGHT IS KEPT (rule 3) by grading each figure to a COMMON target
measured off the ground plate, multiplicatively per channel, so each face keeps
its own modelling while both sit in one light.

  python3 pipeline/beat05_twoguard_composite.py            # dry, prints geometry
  python3 pipeline/beat05_twoguard_composite.py --write

$0. numpy + PIL. No model, no GPU, no network.
"""
from __future__ import annotations

import hashlib
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

GUARD1 = os.path.join(REPO, "taste/refs/guard1-canon-founder-0822.png")
GUARD2 = os.path.join(REPO, "taste/refs/guard2-canon-founder-0822.png")
CANON = os.path.join(REPO, "taste/refs/goblin-canon-founder-0821.png")
OUT = os.path.join(REPO, "farm-out", "ep2-b05-twoguard-src-0822")
W, H = 832, 1216

# ── THE GROUND. The goblin canon's own meadow with the goblin ERASED, which is
# the one empty field in this tree that is already in the show's dialect. The
# erase + interpolate is `author_jerry_lowerbody_0822.bg_fill`, reused rather
# than reimplemented -- it was written for exactly this and its failure mode
# (a nearest-neighbour pull leaving an outline of the removed figure) is
# already fixed there.
FIGURE_POLY = [(420,122),(490,132),(540,165),(572,225),(580,285),(590,308),
               (628,318),(668,347),(636,375),(586,398),(558,408),(548,440),
               (520,468),(500,487),(495,505),(545,512),(578,530),(597,572),
               (605,640),(608,700),(600,760),(586,802),(566,822),(540,840),
               (470,852),(420,854),(360,850),(305,834),(278,818),(262,780),
               (248,720),(240,650),(246,590),(262,545),(292,516),(340,505),
               (345,487),(320,468),(295,438),(282,405),(252,392),(212,325),
               (248,314),(280,300),(268,258),(282,196),(330,148),(378,127)]
LEGS_POLY = [(276,790),(514,790),(516,900),(492,1004),(470,1044),(414,1046),
             (398,1000),(392,990),(346,1006),(298,998),(292,952),(312,930),
             (300,896),(276,882)]

# ── THE TWO FIGURES. `src_box` is the head+shoulders region of each portrait,
# measured on the file; `scale` shrinks a full-frame close-up into a medium
# two-shot; `dest` is where its top-left lands. Integer translation only -- a
# resample of the FIGURE is unavoidable when scaling, but the placement adds no
# second resample on top of it.
FIGS = {
    "g1": {"src": GUARD1, "src_box": (120, 40, 780, 900), "scale": 0.56,
           "dest": (46, 300), "flip": False,
           "why": "guard one, frame LEFT. The bespectacled man; his canon is a "
                  "three-quarter turn toward frame right, which points him "
                  "INTO the frame from the left."},
    "g2": {"src": GUARD2, "src_box": (110, 30, 790, 900), "scale": 0.56,
           "dest": (420, 330), "flip": False,
           "why": "guard two, frame RIGHT and 30px lower, so the two heads do "
                  "not sit on one line -- a level pair reads as a mugshot. The "
                  "dark-haired man, mid-shout, which is the one carrying the "
                  "beat's 'halt and scan'."},
}

# The oval matte, as a fraction of the cut box. Generous on purpose: it carries
# source grass, which lands on destination grass.
OVAL_INSET = 0.02
FEATHER = 34

# The seam mask the naturalize is given. A BAND around each pasted oval -- not
# the whole frame. Doctrine §4 runs composites at padding_mask_crop 64, which
# crops to the mask and spends all 12 denoising steps there; a full-frame mask
# would spread them over a frame that does not need them.
SEAM_GROW = 26
SEAM_BAND = 30


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def bg_fill(img, hole):
    """Row-wise horizontal interpolation across the hole, then a blur."""
    a = np.asarray(img).astype(np.float32)
    h = np.asarray(hole) > 64
    out = a.copy()
    xs = np.arange(W)
    for y in range(H):
        keep = ~h[y]
        if keep.sum() < 8:
            continue
        for k in range(3):
            out[y, h[y], k] = np.interp(xs[h[y]], xs[keep], a[y, keep, k])
    sm = np.stack([ndimage.gaussian_filter(out[..., k], 14) for k in range(3)],
                  axis=-1)
    w = np.clip(ndimage.gaussian_filter(h.astype(np.float32), 10) * 1.6, 0, 1)
    return Image.fromarray(np.clip(
        out * (1 - w[..., None]) + sm * w[..., None], 0, 255).astype(np.uint8))


def ground():
    """The empty meadow: the canon with its figure erased and interpolated."""
    src = Image.open(CANON).convert("RGB")
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.polygon(FIGURE_POLY, fill=255)
    d.polygon(LEGS_POLY, fill=255)
    m = m.filter(ImageFilter.MaxFilter(9))
    m = Image.fromarray((np.asarray(m.filter(ImageFilter.GaussianBlur(9))) > 12)
                        .astype(np.uint8) * 255)
    return bg_fill(src, m)


def grade(patch, alpha, target):
    """Match a figure to the ground's light, PER CHANNEL, multiplicatively.

    Multiplicative and per-channel is a von Kries diagonal: it moves the
    figure's white point onto the plate's without touching the RATIOS inside
    any one pixel's neighbourhood, so each face keeps its own modelling -- the
    lit rim stays lit, the shaded side stays shaded. That is doctrine rule 3
    ("the plate's own light is kept") applied to a figure instead of a texture.
    Measured only where the matte is actually opaque, so the surround the oval
    carried does not drag the average.
    """
    a = np.asarray(patch).astype(np.float32)
    w = (np.asarray(alpha).astype(np.float32) / 255.0)[..., None]
    core = w > 0.85
    if core.sum() < 500:
        return patch, (1.0, 1.0, 1.0)
    cur = (a * core).sum(axis=(0, 1)) / core.sum(axis=(0, 1))
    gain = np.clip(np.asarray(target, np.float32) / np.maximum(cur, 1e-3),
                   0.75, 1.35)
    return (Image.fromarray(np.clip(a * gain, 0, 255).astype(np.uint8)),
            tuple(round(float(g), 3) for g in gain))


def build():
    gnd = ground()
    ga = np.asarray(gnd).astype(np.float32)
    # The target light: the ground's own mean in the band the figures occupy.
    target = ga[300:1000].reshape(-1, 3).mean(axis=0)

    plate = gnd.copy()
    seam = Image.new("L", (W, H), 0)
    report = []
    for tag, f in FIGS.items():
        src = Image.open(f["src"]).convert("RGB")
        cut = src.crop(f["src_box"])
        if f["flip"]:
            cut = cut.transpose(Image.FLIP_LEFT_RIGHT)
        cw = int(cut.width * f["scale"])
        chh = int(cut.height * f["scale"])
        cut = cut.resize((cw, chh), Image.LANCZOS)

        # the feathered oval
        al = Image.new("L", (cw, chh), 0)
        ix, iy = int(cw * OVAL_INSET), int(chh * OVAL_INSET)
        ImageDraw.Draw(al).ellipse([ix, iy, cw - ix, chh - iy], fill=255)
        al = al.filter(ImageFilter.GaussianBlur(FEATHER))

        cut, gain = grade(cut, al, target)
        plate.paste(cut, f["dest"], al)

        # the seam band: a ring just inside/outside the oval's own edge
        ring = Image.new("L", (W, H), 0)
        ring.paste(al, f["dest"])
        r = np.asarray(ring).astype(np.float32) / 255.0
        band = ((r > 0.06) & (r < 0.94)).astype(np.uint8) * 255
        band = np.asarray(Image.fromarray(band).filter(
            ImageFilter.MaxFilter(2 * (SEAM_GROW // 2) + 1)))
        seam = Image.fromarray(np.maximum(np.asarray(seam), band))
        report.append((tag, f["src_box"], (cw, chh), f["dest"], gain))

    seam = seam.filter(ImageFilter.GaussianBlur(6))
    seam = Image.fromarray((np.asarray(seam) > 40).astype(np.uint8) * 255)
    return plate, seam, report, target


def main():
    write = "--write" in sys.argv
    plate, seam, report, target = build()
    print("ground: the canon's meadow, figure erased and interpolated")
    print("target light (ground mean, y300..1000): R%.1f G%.1f B%.1f" % tuple(target))
    for tag, box, size, dest, gain in report:
        print("  %-3s src_box=%-22s -> %-11s at %-11s gain R%.3f G%.3f B%.3f"
              % (tag, str(box), "%dx%d" % size, str(dest), *gain))
    s = np.asarray(seam)
    print("seam mask: %d px (%.1f%% of frame), rows %d..%d"
          % ((s > 0).sum(), 100.0 * (s > 0).mean(),
             int(np.argmax((s > 0).any(axis=1))),
             H - 1 - int(np.argmax((s > 0).any(axis=1)[::-1]))))
    if not write:
        print("\nDRY -- pass --write to author into %s" % os.path.relpath(OUT, REPO))
        return 0
    os.makedirs(OUT, exist_ok=True)
    for name, im in (("b05-twoguard-init-0822.png", plate),
                     ("b05-twoguard-seam-0822.png", seam)):
        p = os.path.join(OUT, name)
        im.save(p)
        print("WROTE %-34s %s" % (name, sha256_of(p)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
