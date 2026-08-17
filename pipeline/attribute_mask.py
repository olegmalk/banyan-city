#!/usr/bin/env python3
r"""Author the mask that decides WHICH FIGURE carries an attribute. $0, no GPU.

WHY THIS EXISTS -- THE FOUNDER ASKED FOR A MECHANISM, NOT A WORDING.
2026-08-15, on the glasses spread: "draw the second man without glasses. we need
to have control." He was offered two wordings -- drop the wire-rims from two
beats, or draw guard B in glasses too -- and rejected both. What he asked for is
control over which figure carries an attribute, and no wording can give it.

THE REASON NO WORDING CAN, AND IT IS PUBLISHED. `glasses` named inside ONE man's
clause lands on BOTH men, 5 of 5. That is not the prop failure (the bark board
goes to ONE WRONG figure, 3 of 3) and not the garment behaviour (hair and
garments bind to their clause cleanly at the same seed). It is a third class,
which pipeline/loop/attrbind-eyewear-0817.md names BROADCAST: CLIP's text encoder
is causal and its EOS token carries global prompt semantics, so an attribute
token named anywhere is present in the pooled embedding that steers the whole
frame. Nothing in the prompt says WHICH face, and every face qualifies.
  ALE-Edit, arXiv 2412.04715  -- causal encoder + EOS as the leakage mechanism
  MaskAttn-SDXL, arXiv 2509.15357 -- same defect, fixed by a LEARNED mask (training)
  Regional prompting for DiT, arXiv 2411.02395 -- training-free but DiT, not SDXL
And it is why a negative cannot help: leakage is a BINDING failure, not a
presence failure. `wire-rim glasses` BINDS 7 of 7 on beat 09's one-figure
close-up -- the tag is strong and the phrasing is right. It fails only when a
second face exists for it to also land on. THE NUMBER OF ELIGIBLE FACES IS THE
VARIABLE, NOT THE WORDING.

WHAT IS AVAILABLE TO US, RESEARCHED OUTSIDE THIS REPO. There is no drop-in
regional prompting for SDXL in our stack: the diffusers community
`regional_prompting` pipeline is SD1.5 only, MaskAttn-SDXL needs training, and
every mature Attention-Couple implementation is a GPL-3.0/AGPL-3.0 ComfyUI or
Forge extension that licence_gate.py forbids us to vendor. What IS available is
the pattern this tree already proved on the bark clipboard (beats 06 and 10):
put the structure in the init with plain image processing, then let a LOW-strength
masked pass harmonise it. Masked denoising is structural rather than persuasive --
an attribute cannot leak onto guard B if guard B's pixels are never denoised.

SO THE CONTROL LIVES IN THE MASK, AND THIS STEP AUTHORS IT WITH NO SAMPLER IN IT.
Geometry is deterministic, inspectable and diffable; a prompt is none of those.
Splitting mask authoring out from rendering means the question "which pixels may
change?" is answered before a GPU is involved and can be reviewed as a picture.

    python3 attribute_mask.py --init PLATE.png --init-sha256 <hex> --out m.png \
        --add ring:294,369,13,13,3 --add ring:329,377,13,13,3 \
        --add band:307,371,316,374,3 \
        --protect 440,175,580,265 \
        [--dilate 1] [--preview p.png] [--note "..."]

Shapes, add or subtract, in pixels of the init:
    ellipse:cx,cy,rx,ry          a filled blob
    ring:cx,cy,rx,ry,w           an ANNULUS of width w -- a spectacle lens rim,
                                 a band, any outline. The thin-band case is why
                                 --ellipse and --quad were not enough.
    quad:x0,y0,x1,y1,x2,y2,x3,y3 a filled straight-edged polygon
    band:x0,y0,x1,y1,w           a thick line segment -- a bridge, a temple arm
    box:x0,y0,x1,y1              a filled rectangle

--protect IS THE TEETH AND IT IS THE POINT. Every --protect box is a region that
must not change -- guard B's head, the other man's whole figure. If ONE white
pixel of the mask falls inside a protect box the tool REFUSES (exit 5) and names
the overlap. Spend guards in this tree are code rather than intentions, and so is
this one: "we need to have control" is worth something only if the control is
enforced somewhere a mistake cannot get past. A mask that cannot touch guard B is
a stronger promise than any wording, and unlike a wording it is checkable.

WHAT THIS TOOL DOES NOT DECIDE. Whether the resulting plate is SHIPPABLE -- the
look, the framing, whether the wire-rims are the right wire-rims -- is R4 and the
founder's alone. This writes geometry and refuses bad geometry. It scores nothing.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import os
import sys


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ints(spec: str, kind: str, n: int) -> list:
    vals = [int(round(float(v))) for v in spec.split(",")]
    if len(vals) != n:
        raise ValueError("%s wants %d numbers, got %d" % (kind, n, len(vals)))
    return vals


def draw_shape(draw, spec: str, fill: int) -> str:
    """Render one shape spec onto `draw`. Returns a human description."""
    kind, _, rest = spec.partition(":")
    kind = kind.strip().lower()
    if kind == "ellipse":
        cx, cy, rx, ry = _ints(rest, "ellipse", 4)
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)
        return "ellipse centre (%d,%d) radii (%d,%d)" % (cx, cy, rx, ry)
    if kind == "ring":
        cx, cy, rx, ry, w = _ints(rest, "ring", 5)
        # An annulus, drawn as an outlined ellipse of width w. PIL centres the
        # stroke on the path, so the band straddles the radius.
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=fill, width=w)
        return "ring centre (%d,%d) radii (%d,%d) width %d" % (cx, cy, rx, ry, w)
    if kind == "quad":
        v = _ints(rest, "quad", 8)
        draw.polygon(list(zip(v[0::2], v[1::2])), fill=fill)
        return "quad %s" % str(list(zip(v[0::2], v[1::2])))
    if kind == "band":
        x0, y0, x1, y1, w = _ints(rest, "band", 5)
        draw.line([x0, y0, x1, y1], fill=fill, width=w)
        return "band (%d,%d)-(%d,%d) width %d" % (x0, y0, x1, y1, w)
    if kind == "box":
        x0, y0, x1, y1 = _ints(rest, "box", 4)
        draw.rectangle([x0, y0, x1, y1], fill=fill)
        return "box [%d,%d,%d,%d]" % (x0, y0, x1, y1)
    raise ValueError("unknown shape %r (want ellipse/ring/quad/band/box)" % kind)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--init", required=True, help="the plate the mask is for")
    ap.add_argument("--init-sha256", required=True,
                    help="asserted before anything is written; a mismatch is a "
                         "hard stop. A mask is geometry measured against SPECIFIC "
                         "pixels and is meaningless against any other frame.")
    ap.add_argument("--out", required=True, help="mask PNG to write")
    ap.add_argument("--add", action="append", default=[],
                    help="shape to include; repeatable")
    ap.add_argument("--sub", action="append", default=[],
                    help="shape to cut back out, applied after every --add; "
                         "repeatable. This is the board-MINUS-the-hand case.")
    ap.add_argument("--protect", action="append", default=[],
                    help="x0,y0,x1,y1 that MUST NOT change; repeatable. One "
                         "white pixel inside it and this tool refuses.")
    ap.add_argument("--dilate", type=int, default=0,
                    help="grow the mask by N px (MaxFilter). Applied before the "
                         "protect check, so growth cannot sneak past it.")
    ap.add_argument("--preview", default="",
                    help="write a look-at-it PNG: the plate with the mask "
                         "tinted and every protect box outlined")
    ap.add_argument("--composite", default="",
                    help="ALSO write the init with the --add geometry INKED IN, "
                         "to be used as the init of a LOW-strength masked pass. "
                         "This is the half that makes the attribute ours rather "
                         "than the model's: with the shape already in the init, "
                         "the sampler is asked to harmonise a frame that exists, "
                         "not to invent one. At strength 0.2-0.35 only "
                         "steps x strength steps run, so the inked structure "
                         "survives. The bark clipboard split at 0.45 and held at "
                         "0.30 for the same reason. The composite is drawn from "
                         "the UNDILATED shapes while the mask is dilated, so the "
                         "harmoniser gets a margin of real plate pixels to blend "
                         "into on both sides of the ink.")
    ap.add_argument("--ink", default="auto",
                    help="R,G,B for the composited geometry, or 'auto' (default) "
                         "to SAMPLE THE PLATE'S OWN DARKEST LINEART inside the "
                         "mask bbox. Auto is the right default because colour "
                         "does not travel between backends and a hand-picked "
                         "black is a guess about a dialect we can simply measure.")
    ap.add_argument("--note", default="")
    a = ap.parse_args()

    if not os.path.isfile(a.init):
        print("!! init not found: %s" % a.init, flush=True)
        return 2
    have = sha256_of(a.init)
    if have != a.init_sha256:
        print("!! INIT SHA MISMATCH -- refusing.\n   want %s\n   have %s"
              % (a.init_sha256, have), flush=True)
        return 3
    if not a.add:
        print("!! no --add shapes; an all-black mask redraws nothing.", flush=True)
        return 2

    from PIL import Image, ImageDraw, ImageFilter

    plate = Image.open(a.init).convert("RGB")
    W, H = plate.size
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)

    described = []
    try:
        for spec in a.add:
            described.append("add " + draw_shape(d, spec, 255))
        for spec in a.sub:
            described.append("sub " + draw_shape(d, spec, 0))
    except ValueError as exc:
        print("!! %s" % exc, flush=True)
        return 2

    # The ink follows the shapes as drawn; the MASK may then be grown. Keeping
    # them separate is what leaves real plate pixels either side of the ink for
    # the harmoniser to blend into.
    undilated = mask.point(lambda v: 255 if v > 0 else 0)

    if a.dilate > 0:
        mask = mask.filter(ImageFilter.MaxFilter(2 * a.dilate + 1))
        described.append(
            "dilate %d px (mask only -- the ink is not dilated)" % a.dilate)

    binary = mask.point(lambda v: 255 if v > 0 else 0)
    box = binary.getbbox()
    if box is None:
        print("!! the --sub shapes cancelled every --add; mask is empty.", flush=True)
        return 4
    bbox = [box[0], box[1], box[2] - 1, box[3] - 1]   # getbbox is exclusive
    # histogram() rather than getdata(): exact, and not deprecated in Pillow 12.
    white = W * H - binary.histogram()[0]

    # --- the control check, and it is arithmetic rather than an opinion --------
    protect = []
    for spec in a.protect:
        try:
            protect.append(_ints(spec, "protect", 4))
        except ValueError as exc:
            print("!! %s" % exc, flush=True)
            return 2
    violations = []
    for (x0, y0, x1, y1) in protect:
        region = binary.crop((max(0, x0), max(0, y0),
                              min(W, x1 + 1), min(H, y1 + 1)))
        hit = (region.size[0] * region.size[1]) - region.histogram()[0]
        if hit:
            violations.append(((x0, y0, x1, y1), hit))
    for (bx, hit) in violations:
        print("!! MASK ENTERS A PROTECTED REGION [%d,%d,%d,%d]: %d px."
              % (bx[0], bx[1], bx[2], bx[3], hit), flush=True)
    if violations:
        print("!! refusing. The point of this step is that the protected figure "
              "CANNOT be changed; a mask that reaches him is the defect, not the "
              "fix. Move the geometry, do not widen the promise.", flush=True)
        return 5

    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    mask.save(a.out)

    # --- the composite: ink the geometry into the plate ------------------------
    composite_sha = ""
    ink = None
    if a.composite:
        if a.ink.strip().lower() == "auto":
            # The plate's own darkest lineart inside the region. Measured, not
            # guessed: a hand-picked black is a claim about a dialect, and this
            # tree has already learned that colour does not travel.
            region = plate.crop((bbox[0], bbox[1], bbox[2] + 1, bbox[3] + 1))
            px = list(region.convert("RGB").getdata())
            ink = min(px, key=lambda t: t[0] + t[1] + t[2])
        else:
            try:
                r, g, b = _ints(a.ink, "ink", 3)
                ink = (r, g, b)
            except ValueError as exc:
                print("!! %s" % exc, flush=True)
                return 2
        comp = plate.copy()
        comp.paste(Image.new("RGB", (W, H), ink), (0, 0), undilated)
        os.makedirs(os.path.dirname(os.path.abspath(a.composite)) or ".",
                    exist_ok=True)
        comp.save(a.composite)
        composite_sha = sha256_of(a.composite)
        # The composite must be byte-identical to the plate everywhere the ink is
        # not. That is the same promise as --protect and it is worth asserting
        # rather than assuming, because this file becomes the init of a render.
        import itertools
        changed = sum(1 for o, n, m in itertools.zip_longest(
            plate.convert("RGB").getdata(), comp.getdata(), undilated.getdata())
            if o != n and not m)
        if changed:
            print("!! composite changed %d px OUTSIDE the inked geometry -- "
                  "refusing, the init of a render must not drift." % changed,
                  flush=True)
            return 6
        print("COMPOSITE %s  ink=%s  changed only inside the geometry"
              % (a.composite, str(ink)), flush=True)

    preview_path = a.preview
    if preview_path:
        prev = plate.copy()
        tint = Image.new("RGB", (W, H), (255, 0, 128))
        prev.paste(tint, (0, 0), binary.point(lambda v: 140 if v > 0 else 0))
        pd = ImageDraw.Draw(prev)
        for (x0, y0, x1, y1) in protect:
            pd.rectangle([x0, y0, x1, y1], outline=(0, 255, 255), width=2)
        os.makedirs(os.path.dirname(os.path.abspath(preview_path)) or ".",
                    exist_ok=True)
        prev.save(preview_path)

    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sidecar = a.out + ".meta.yaml"
    with open(sidecar, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join([
            "# Mask provenance, written by pipeline/attribute_mask.py. NO SAMPLER",
            "# AND NO GPU WAS INVOLVED -- this file is pure geometry, which is why",
            "# it can be diffed and argued with before any pixel is spent.",
            "tool: pipeline/attribute_mask.py",
            "init_image: %s" % a.init.replace("\\", "/"),
            "init_sha256: %s" % have,
            "init_size: %dx%d" % (W, H),
            "mask_png: %s" % os.path.basename(a.out),
            "mask_sha256: %s" % sha256_of(a.out),
            "mask_white_px: %d" % white,
            "mask_frame_frac: %.5f" % (white / float(W * H)),
            "mask_bbox_px: [%d, %d, %d, %d]" % tuple(bbox),
            "shapes:",
            "\n".join("  - %s" % s for s in described),
            "protect_boxes_px: %s" % (str([list(p) for p in protect]) or "[]"),
            "protect_violations: 0",
            "composite_png: %s" % (os.path.basename(a.composite) or "null"),
            "composite_sha256: %s" % (composite_sha or "null"),
            "composite_ink_rgb: %s" % (str(list(ink)) if ink else "null"),
            "composite_ink_source: %s"
            % ("sampled: the plate's own darkest pixel inside the mask bbox"
               if (a.composite and a.ink.strip().lower() == "auto")
               else ("given on the command line" if a.composite else "null")),
            "preview_png: %s" % (os.path.basename(preview_path) or "null"),
            "authored_utc: %s" % stamp,
            "cost_usd: 0",
            "geometry_is_the_stewards: >-",
            "  THE GEOMETRY IS THE STEWARD'S, NOT THE FOUNDER'S. He asked for",
            "  control over which figure carries an attribute; he did not specify",
            "  a pixel. Every number above is the steward's and is the first",
            "  thing a correction should move.",
            "note: >-",
            "  %s" % (a.note or "attribute region mask"),
            "",
        ]))

    print("MASK %s  white=%d px (%.3f%% of frame)  bbox=[%d,%d,%d,%d]"
          % (a.out, white, 100.0 * white / (W * H), *bbox), flush=True)
    for s in described:
        print("   %s" % s, flush=True)
    print("PROTECTED %d region(s), 0 violations" % len(protect), flush=True)
    if preview_path:
        print("WROTE %s" % preview_path, flush=True)
    print("WROTE %s" % sidecar, flush=True)
    print("rc=0 cost_usd=0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
