#!/usr/bin/env python3
"""leaf_count_composite.py -- give the init its leaf COUNT with plain image
processing, so the sampler never has to invent one.

WHY THIS EXISTS
---------------
Exact instance count is a measured failure of text-to-image diffusion, not a
wording problem we have not yet phrased well enough:

  * "Text-to-Image Diffusion Models Cannot Count, and Prompt Refinement Cannot
    Help", arXiv:2503.06884 -- prompt refinement generally does NOT improve
    counting accuracy.
  * "Make It Count", CVPR 2025 (arXiv:2406.10210), implemented on SDXL, which is
    our stills model: plain SDXL with a numeral in the prompt scores 26-28%
    counting accuracy. Their fix reaches 54% and needs a ReLayout U-Net trained
    on ~10K image pairs. The field's accepted decomposition is text -> LAYOUT ->
    image: count is a layout problem.
  * That paper's objection to Bounded Attention -- it "requires users to
    manually provide the bounding boxes" -- is our whole opportunity. We are not
    generating a random scene. We are drawing ONE designed character whose
    layout we already know, so we can simply provide it.

Our own evidence agrees. `authored_b01_canon_0816` asks for "exactly two wide
oval cotyledon leaves" AND bans "no three leaves, no four leaves, no many
leaves" -- the strongest wording available, numeral plus explicit negation of
every wrong count -- and returned 0 of 16 frames with two leaves on 2026-08-17.
`authored_b21_scale_0816` returned 2 of 4. The vacancy law already recorded here
says why the negation cannot work: an empty region is a hole the model fills
with the largest noun, and the negative does not reach it.

So this tool does the layout step, in PIL, with no model and no GPU. It takes a
real rendered plate that has the right style and the right height relation but
too many leaves, and it REMOVES the extra leaves by patching them with the
plate's own background pixels. The count is then correct BY CONSTRUCTION, before
any sampler runs. A following LOW-strength inpaint (0.30) only blends the seam.

This is the bark-clipboard pattern from beats 06 and 10, generalised: give the
init its structure with plain image processing, then inpaint at LOW strength,
because asking the sampler to invent the structure destroys what it sits on.
Community practice puts 0.2-0.35 denoise in the band that preserves layout and
identity (stable-diffusion-art.com/denoising-strength, learn.rundiffusion.com).

Crucially, the patch is copied from the plate's OWN pixels rather than left
empty. An emptied region is exactly the vacancy the model would fill with
another leaf. There is nothing here for it to fill.

$0: no model, no network, no GPU. Deterministic -- same arguments, same bytes.

THE RESIDUAL-LAMINA FAULT, AND THE 2026-08-17 FIX (additive, opt-in)
-------------------------------------------------------------------
The first four composites this tool made (review/leaf-count-0817/comp-s*.png,
cccbc85f) reused ONE hand-fitted `--remove` geometry across four seeds. Two of
them -- s0 and s2 -- kept a dark lamina below the junction: the shaded proximal
half of the blade whose bright tip was patched, which the leaf-count bar's own
counting rules ("any partly occluded blade whose outline is identifiable") would
score as a THIRD BLADE. s1 and s3 did not. That is a 50% defect rate, and it was
invisible to the tool: measured on s0, only 9% of the surviving dark pixels lay
inside the declared hard ellipse, so the declared region never covered the object
it claimed to remove and NOTHING IN THE TOOL MEASURED THAT.

Root cause: one geometry, four different blades. The house pattern already names
the rule this broke -- "FITTED TO THE OBJECT, NOT TO THE MASK"
(pipeline/composite-init-pattern.md section 3).

The fix is two additions, both opt-in so that every previously-committed
invocation still reproduces byte-identically (regression-checked: all four
comp-s*.png hash unchanged when the new flags are absent):

  1. `--check` MEASURES what survived. Inside the declared removal footprint
     (dilated by --check-margin) it finds pixels that still match a declared
     OBJECT RULE (--object-dark / --object-gmr-min / --object-gmr-max, measured
     per plate -- the pattern doc's warning that no colour rule has ever
     transferred between plates applies here too), groups them into 4-connected
     components, and prints every component >= --residual-min-area with its area
     and bbox. `--assert-clear` then REFUSES TO WRITE when a component survives,
     so this defect cannot reach a canon plate silently again.
  2. `--sweep` PATCHES what survived, fitted to the component's own silhouette
     (dilated by --sweep-grow, feathered) rather than to another guessed
     ellipse, from the same background source. It repeats up to --sweep-passes.

Both stages skip pixels inside any `--protect` region, which is how structure
that must survive (a stem, a keeper blade) is kept out of the sweep's way.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover
    sys.exit("!! needs Pillow: pip install pillow")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_ellipse(spec: str) -> tuple[int, int, int, int, float]:
    """cx,cy,rx,ry[,angle_degrees]"""
    parts = [p.strip() for p in spec.split(",") if p.strip() != ""]
    if len(parts) not in (4, 5):
        raise SystemExit(
            "!! --remove wants cx,cy,rx,ry[,angle], got %r" % spec)
    cx, cy, rx, ry = (int(round(float(p))) for p in parts[:4])
    angle = float(parts[4]) if len(parts) == 5 else 0.0
    if rx <= 0 or ry <= 0:
        raise SystemExit("!! --remove radii must be positive, got %r" % spec)
    return cx, cy, rx, ry, angle


def parse_offset(spec: str) -> tuple[int, int]:
    parts = [p.strip() for p in spec.split(",")]
    if len(parts) != 2:
        raise SystemExit("!! --source-offset wants dx,dy, got %r" % spec)
    return int(round(float(parts[0]))), int(round(float(parts[1])))


def ellipse_mask(size, cx, cy, rx, ry, angle, feather):
    """A white filled ellipse on black, optionally rotated, then feathered."""
    # Draw upright at 4x on a tight canvas, rotate, paste. 4x keeps the edge
    # smooth: a rotated hard ellipse at 1x staircases, and the staircase
    # survives the blur as a visible ridge in the blend.
    ss = 4
    pad = int(max(rx, ry) * 1.6) + 8
    tile = Image.new("L", ((pad * 2) * ss, (pad * 2) * ss), 0)
    d = ImageDraw.Draw(tile)
    d.ellipse(
        [(pad - rx) * ss, (pad - ry) * ss, (pad + rx) * ss, (pad + ry) * ss],
        fill=255,
    )
    tile = tile.resize((pad * 2, pad * 2), Image.LANCZOS)
    if angle:
        tile = tile.rotate(angle, resample=Image.BICUBIC, expand=False)
    mask = Image.new("L", size, 0)
    mask.paste(tile, (cx - pad, cy - pad), tile)
    if feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(feather))
    return mask


def diffuse_fill(img, hard_mask, iters: int, radius: float):
    """Fill the masked region from ITS OWN BOUNDARY, keeping the plate's light.

    A shifted clone cannot serve a plate with a strong luminance gradient: on
    beat 21's dawn plate the best available lateral offset still left an
    out-of-sample boundary-ring MAE of 22.9, and fitting a gain/offset or a plane
    on the inner ring made it worse out of sample (27.8 / 26.3). Copying is also
    decal tell #4, a visible repeat.

    So the fill is PROCEDURAL: blur the whole frame, keep only the part inside the
    region, repeat. Outside pixels never move, so each pass pulls the boundary's
    own colour and gradient inward and the region converges to a smooth
    interpolation of its own surroundings -- the plate's own light by
    construction, no clone, no import. Deterministic: same arguments, same bytes.

    The vacancy law is satisfied: the region is FILLED with plausible background,
    never left empty. What it is not is textured -- that is the 0.30 pass's job,
    and it is the reason the blend mask must cover the filled region.
    """
    out = img.copy()
    for _ in range(int(iters)):
        out = Image.composite(
            out.filter(ImageFilter.GaussianBlur(radius)), out, hard_mask)
    return out


def parse_box(spec: str) -> tuple[int, int, int, int]:
    """x0,y0,x1,y1 -- half-open, as PIL crop boxes are."""
    parts = [p.strip() for p in spec.split(",") if p.strip() != ""]
    if len(parts) != 4:
        raise SystemExit("!! wants x0,y0,x1,y1, got %r" % spec)
    x0, y0, x1, y1 = (int(round(float(p))) for p in parts)
    if x1 <= x0 or y1 <= y0:
        raise SystemExit("!! empty box %r" % spec)
    return x0, y0, x1, y1


def in_any_box(x: int, y: int, boxes) -> bool:
    for x0, y0, x1, y1 in boxes:
        if x0 <= x < x1 and y0 <= y < y1:
            return True
    return False


def object_pixels(img, regions, protect, dark, bright, gmr_min, gmr_max):
    """Pixels matching the declared OBJECT RULE inside `regions`, outside `protect`.

    The rule is deliberately explicit and per-plate. No colour rule in this repo
    has ever transferred between plates (composite-init-pattern.md section 5), so
    the caller states the numbers and this function only applies them.
    """
    px = img.load()
    W, H = img.size
    found = set()
    for x0, y0, x1, y1 in regions:
        for y in range(max(0, y0), min(H, y1)):
            for x in range(max(0, x0), min(W, x1)):
                if protect and in_any_box(x, y, protect):
                    continue
                r, g, b = px[x, y]
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                if dark is not None and lum >= dark:
                    continue
                if bright is not None and lum <= bright:
                    continue
                gmr = g - r
                if gmr_min is not None and gmr < gmr_min:
                    continue
                if gmr_max is not None and gmr > gmr_max:
                    continue
                found.add((x, y))
    return found


def components(pixels):
    """4-connected components of a pixel set, largest first.

    Returns [(area, (x0, y0, x1, y1), [pixels...]), ...]. Pure stdlib: this tool
    is payloaded inline to the box, where PIL is the only dependency we assume.
    """
    todo = set(pixels)
    out = []
    while todo:
        seed = todo.pop()
        stack = [seed]
        blob = [seed]
        x0 = x1 = seed[0]
        y0 = y1 = seed[1]
        while stack:
            x, y = stack.pop()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) in todo:
                    todo.discard((nx, ny))
                    stack.append((nx, ny))
                    blob.append((nx, ny))
                    x0 = min(x0, nx); x1 = max(x1, nx)
                    y0 = min(y0, ny); y1 = max(y1, ny)
        out.append((len(blob), (x0, y0, x1 + 1, y1 + 1), blob))
    out.sort(key=lambda c: (-c[0], c[1]))
    return out


def silhouette_mask(size, blobs, grow, feather, protect):
    """A mask fitted to the residual's OWN shape, grown and feathered.

    Fitted to the object, not to a second guessed ellipse -- which is the rule
    the original one-ellipse-for-four-seeds invocation broke.
    """
    m = Image.new("L", size, 0)
    px = m.load()
    for blob in blobs:
        for x, y in blob:
            px[x, y] = 255
    if grow > 0:
        m = m.filter(ImageFilter.MaxFilter(2 * grow + 1))
    if feather > 0:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    if protect:
        d = ImageDraw.Draw(m)
        for x0, y0, x1, y1 in protect:
            d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=0)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(
        description="patch extra leaves out of a plate with its own background "
                    "pixels, so leaf count is correct BEFORE any sampler runs")
    ap.add_argument("--init", required=True,
                    help="the rendered plate to correct")
    ap.add_argument("--out", required=True,
                    help="composited init (leaf count correct by construction)")
    ap.add_argument("--mask-out", default=None,
                    help="write the union mask here, for inpaint_fruit --mask-png")
    ap.add_argument("--remove", action="append", default=[], metavar="cx,cy,rx,ry[,ang]",
                    help="an extra leaf to patch out; repeatable")
    ap.add_argument("--remove-auto", action="append", default=[], metavar="x0,y0,x1,y1",
                    help="an extra leaf to patch out, SEGMENTED inside this box "
                         "with the object rule and patched to its own silhouette "
                         "instead of to a guessed ellipse. Repeatable. Needs an "
                         "object rule; honours --protect. Use this when the blade "
                         "is a curve no ellipse fits -- an ellipse over a curved "
                         "leaf either misses its tip or eats the stem")
    ap.add_argument("--source-offset", action="append", default=[], metavar="dx,dy",
                    help="where to copy background from for the matching --remove. "
                         "Given once, it applies to every --remove.")
    ap.add_argument("--feather", type=int, default=9,
                    help="gaussian blur on the patch mask, px (default 9)")
    ap.add_argument("--mask-grow", type=int, default=12,
                    help="dilate the mask written by --mask-out beyond the patch, "
                         "px, so the blend pass covers the whole seam (default 12)")
    # --- residual check and sweep (2026-08-17). Opt-in: absent, this tool
    # behaves exactly as it did at commit 07840029, byte for byte. ---
    ap.add_argument("--check", action="store_true",
                    help="measure what SURVIVED the patch inside the removal "
                         "footprint and print every residual component")
    ap.add_argument("--check-region", action="append", default=[], metavar="x0,y0,x1,y1",
                    help="where to look for residual; repeatable. Default: the "
                         "bbox of the removal masks grown by --check-margin")
    ap.add_argument("--check-margin", type=int, default=24,
                    help="grow the default check region beyond the patch, px "
                         "(default 24) -- the residual lives just OUTSIDE the "
                         "declared ellipse, which is the whole fault")
    ap.add_argument("--protect", action="append", default=[], metavar="x0,y0,x1,y1",
                    help="never check and never patch inside this box; how a "
                         "stem or a keeper blade is kept out of the sweep")
    ap.add_argument("--object-dark", type=float, default=None,
                    help="OBJECT RULE: luminance strictly below this is object")
    ap.add_argument("--object-bright", type=float, default=None,
                    help="OBJECT RULE: luminance strictly above this is object")
    ap.add_argument("--object-gmr-min", type=float, default=None,
                    help="OBJECT RULE: (G-R) at or above this is object. Measure "
                         "it on THIS plate -- no colour rule here has ever "
                         "transferred between plates")
    ap.add_argument("--object-gmr-max", type=float, default=None,
                    help="OBJECT RULE: (G-R) at or below this is object")
    ap.add_argument("--residual-min-area", type=int, default=120,
                    help="components smaller than this are noise, not a blade "
                         "(default 120 px)")
    ap.add_argument("--auto-min-area", type=int, default=None,
                    help="minimum segment area for --remove-auto (default: "
                         "--residual-min-area). Separate because a thin blade can "
                         "be smaller than the residual you are willing to gate on")
    ap.add_argument("--sweep", action="store_true",
                    help="PATCH the residual components the check found, fitted "
                         "to their own silhouette, from --source-offset")
    ap.add_argument("--sweep-grow", type=int, default=4,
                    help="dilate each residual silhouette before patching, px")
    ap.add_argument("--sweep-passes", type=int, default=2,
                    help="re-check and re-sweep this many times at most")
    ap.add_argument("--sweep-offset", default=None, metavar="dx,dy",
                    help="background source for the sweep (default: the first "
                         "--source-offset). THE SOURCE LAW: the sweep refuses to "
                         "run when the source itself satisfies the object rule -- "
                         "patching a leaf with pixels that read as a leaf is why "
                         "the first sweep of this plate diverged instead of "
                         "converging (residual 741 -> 867 -> 957 px on seed s2)")
    ap.add_argument("--assert-clear", action="store_true",
                    help="EXIT NONZERO instead of writing if any residual "
                         "component >= --residual-min-area survives. This is the "
                         "guard that stops a 50%% compositor defect reaching a "
                         "canon plate")
    ap.add_argument("--mask-add", action="append", default=[], metavar="cx,cy,rx,ry[,ang]",
                    help="add this ellipse to the BLEND mask without patching a "
                         "pixel of it. This is how the following low-strength pass "
                         "is allowed to reach the KEEPER blades and the junction: a "
                         "mask over the patched vacancy alone would guarantee the "
                         "count by construction and measure nothing, because merge "
                         "and split can only happen where the sampler runs")
    ap.add_argument("--fill", choices=("clone", "diffuse"), default="clone",
                    help="where patched pixels come from. `clone` (default, and "
                         "what every committed composite used) copies the plate "
                         "shifted by --source-offset. `diffuse` fills each region "
                         "from its own boundary ring, which is the only option "
                         "that survives a strong luminance gradient -- on beat "
                         "21's dawn plate no lateral offset got the out-of-sample "
                         "ring MAE below 22.9, and a gain/offset or plane fit made "
                         "it worse")
    ap.add_argument("--fill-iters", type=int, default=80,
                    help="diffuse-fill passes (default 80)")
    ap.add_argument("--fill-radius", type=float, default=8.0,
                    help="diffuse-fill blur radius per pass, px (default 8)")
    ap.add_argument("--note", default="")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan and the arithmetic, write nothing")
    args = ap.parse_args()

    if not args.remove and not args.remove_auto:
        raise SystemExit(
            "!! nothing to do: pass at least one --remove or --remove-auto")
    if not args.source_offset and args.fill != "diffuse":
        raise SystemExit(
            "!! --source-offset is REQUIRED. Leaving the region empty is the "
            "vacancy the model fills with another leaf -- the patch must carry "
            "real background pixels. (`--fill diffuse` satisfies the same law by "
            "synthesising background from the region's own boundary instead.)")
    if (args.fill == "clone" and args.remove
            and len(args.source_offset) not in (1, len(args.remove))):
        raise SystemExit(
            "!! give one --source-offset for all %d --remove, or one each; got %d"
            % (len(args.remove), len(args.source_offset)))
    if args.remove_auto and not any(v is not None for v in (
            args.object_dark, args.object_bright,
            args.object_gmr_min, args.object_gmr_max)):
        raise SystemExit(
            "!! --remove-auto segments the blade with the OBJECT RULE, so it "
            "needs at least one of --object-dark / --object-bright / "
            "--object-gmr-min / --object-gmr-max, measured on THIS plate.")

    init_sha = sha256_of(args.init)
    src = Image.open(args.init).convert("RGB")
    W, H = src.size
    print("init        %s" % args.init)
    print("init size   %dx%d" % (W, H))
    print("init sha256 %s" % init_sha)

    regions = [parse_ellipse(r) for r in args.remove]
    offsets = [parse_offset(o) for o in args.source_offset]
    if not offsets:
        offsets = [(0, 0)]
    if len(offsets) == 1:
        offsets = offsets * max(1, len(regions))

    out = src.copy()
    union = Image.new("L", (W, H), 0)

    for i, ((cx, cy, rx, ry, ang), (dx, dy)) in enumerate(zip(regions, offsets)):
        if dx == 0 and dy == 0 and args.fill != "diffuse":
            raise SystemExit(
                "!! --source-offset 0,0 for region %d copies the leaf onto "
                "itself and changes nothing." % i)
        m = ellipse_mask((W, H), cx, cy, rx, ry, ang, args.feather)
        if args.fill == "diffuse":
            hard = ellipse_mask((W, H), cx, cy, rx, ry, ang, 0)
            need = m.getbbox()
            out = Image.composite(
                diffuse_fill(out, hard, args.fill_iters, args.fill_radius),
                out, m)
            union = Image.composite(Image.new("L", (W, H), 255), union, m)
            print("remove[%d]   ellipse cx=%d cy=%d rx=%d ry=%d ang=%.1f  "
                  "<- DIFFUSE FILL from its own boundary (%d passes, r=%.1f)  "
                  "(mask bbox %s)"
                  % (i, cx, cy, rx, ry, ang, args.fill_iters, args.fill_radius,
                     need))
            continue
        # The source patch is the SAME plate shifted by the offset, so every
        # pixel laid down is real background from this exact frame -- same
        # palette, same grain, same light. Nothing is invented and nothing is
        # left blank.
        shifted = Image.new("RGB", (W, H))
        shifted.paste(src, (dx, dy))
        # Any part of the shifted copy that falls outside the frame is empty;
        # refuse rather than paste black into the plate.
        need = m.getbbox()
        if need is None:
            raise SystemExit("!! region %d produced an empty mask" % i)
        x0, y0, x1, y1 = need
        if not (0 <= x0 - dx and x1 - dx <= W and 0 <= y0 - dy and y1 - dy <= H):
            raise SystemExit(
                "!! region %d: source-offset %d,%d reads outside the frame for "
                "mask bbox %s -- it would paste black into the plate. Pick an "
                "offset that keeps the source patch inside %dx%d."
                % (i, dx, dy, need, W, H))
        out = Image.composite(shifted, out, m)
        union = Image.composite(Image.new("L", (W, H), 255), union, m)
        print("remove[%d]   ellipse cx=%d cy=%d rx=%d ry=%d ang=%.1f  "
              "<- background from offset %+d,%+d  (mask bbox %s)"
              % (i, cx, cy, rx, ry, ang, dx, dy, need))

    # ---- object-fitted removal (--remove-auto) -----------------------------
    # An ellipse over a curved blade either stops short of its tip or eats the
    # stem. Here the blade is SEGMENTED inside a declared box with the object
    # rule and patched to its own silhouette, which is the pattern doc's rule 2
    # ("fitted to the object, not to the mask") done properly.
    auto_log = []
    if args.remove_auto:
        protect_auto = [parse_box(p) for p in args.protect]
        adx, ady = offsets[0] if offsets else (0, 0)
        for i, spec in enumerate(args.remove_auto):
            bx = parse_box(spec)
            comps = [c for c in components(
                object_pixels(src, [bx], protect_auto, args.object_dark,
                              args.object_bright, args.object_gmr_min,
                              args.object_gmr_max))
                if c[0] >= (args.auto_min_area
                            if args.auto_min_area is not None
                            else args.residual_min_area)]
            if not comps:
                raise SystemExit(
                    "!! --remove-auto %s found nothing >= %d px under the object "
                    "rule. Re-derive the rule on this plate, or widen the box."
                    % (spec, args.auto_min_area
                       if args.auto_min_area is not None
                       else args.residual_min_area))
            m = silhouette_mask((W, H), [c[2] for c in comps],
                                args.sweep_grow, args.feather, protect_auto)
            need = m.getbbox()
            if args.fill == "diffuse":
                hard = silhouette_mask((W, H), [c[2] for c in comps],
                                       args.sweep_grow, 0, protect_auto)
                patch = diffuse_fill(out, hard, args.fill_iters, args.fill_radius)
            else:
                if not (0 <= need[0] - adx and need[2] - adx <= W
                        and 0 <= need[1] - ady and need[3] - ady <= H):
                    raise SystemExit(
                        "!! remove-auto[%d]: source-offset %+d,%+d reads outside "
                        "the frame for bbox %s" % (i, adx, ady, need))
                patch = Image.new("RGB", (W, H))
                patch.paste(src, (adx, ady))
            out = Image.composite(patch, out, m)
            union = Image.composite(Image.new("L", (W, H), 255), union, m)
            print("remove-auto[%d] box %s -> %d segment(s), %d px, mask bbox %s "
                  "<- %s"
                  % (i, bx, len(comps), sum(c[0] for c in comps), need,
                     "DIFFUSE FILL from its own boundary (%d passes, r=%.1f)"
                     % (args.fill_iters, args.fill_radius)
                     if args.fill == "diffuse"
                     else "background from %+d,%+d" % (adx, ady)))
            for area, bbox, _ in comps:
                print("     segment   area %5d px  bbox %s" % (area, bbox))
            auto_log.append({
                "box": "%d,%d,%d,%d" % bx,
                "segments": [{"area": a, "bbox": list(b)} for a, b, _ in comps],
                "mask_bbox": list(need),
                "source_offset": "%d,%d" % (adx, ady),
            })

    # ---- residual check / sweep -------------------------------------------
    # The fault this closes: one hand-fitted ellipse was reused across four
    # seeds and covered the blade on only two of them, with nothing measuring
    # the miss. Now the survivor is measured, optionally patched to its own
    # silhouette, and (with --assert-clear) able to stop the job.
    residual_log = {"rule": None, "regions": [], "passes": [], "final": None}
    if args.sweep or args.check or args.assert_clear:
        rule_given = any(v is not None for v in (
            args.object_dark, args.object_bright,
            args.object_gmr_min, args.object_gmr_max))
        if not rule_given:
            raise SystemExit(
                "!! --check/--sweep/--assert-clear need an OBJECT RULE: give at "
                "least one of --object-dark / --object-bright / --object-gmr-min "
                "/ --object-gmr-max, measured on THIS plate.")
        protect = [parse_box(p) for p in args.protect]
        if args.check_region:
            check_regions = [parse_box(r) for r in args.check_region]
        else:
            bb = union.getbbox()
            if bb is None:
                raise SystemExit("!! no patch footprint to check")
            g = args.check_margin
            check_regions = [(max(0, bb[0] - g), max(0, bb[1] - g),
                              min(W, bb[2] + g), min(H, bb[3] + g))]
        residual_log["rule"] = {
            "object_dark": args.object_dark, "object_bright": args.object_bright,
            "object_gmr_min": args.object_gmr_min,
            "object_gmr_max": args.object_gmr_max,
            "residual_min_area": args.residual_min_area,
            "auto_min_area": args.auto_min_area,
        }
        residual_log["regions"] = ["%d,%d,%d,%d" % r for r in check_regions]
        residual_log["protect"] = ["%d,%d,%d,%d" % p for p in protect]
        print("\nRESIDUAL CHECK  rule: lum<%s lum>%s (G-R)>=%s (G-R)<=%s  "
              "min-area %d px" % (args.object_dark, args.object_bright,
                                  args.object_gmr_min, args.object_gmr_max,
                                  args.residual_min_area))
        for r in check_regions:
            print("  check region %s" % (r,))
        for p in protect:
            print("  protect      %s" % (p,))

        sdx, sdy = parse_offset(args.sweep_offset) if args.sweep_offset else offsets[0]
        if args.sweep and args.fill == "clone":
            src_boxes = []
            for x0, y0, x1, y1 in check_regions:
                sb = (x0 - sdx, y0 - sdy, x1 - sdx, y1 - sdy)
                if sb[0] < 0 or sb[1] < 0 or sb[2] > W or sb[3] > H:
                    raise SystemExit(
                        "!! sweep source %+d,%+d reads outside the frame for "
                        "check region %s" % (sdx, sdy, (x0, y0, x1, y1)))
                src_boxes.append(sb)
            dirty = [c for c in components(
                object_pixels(src, src_boxes, [], args.object_dark,
                              args.object_bright, args.object_gmr_min,
                              args.object_gmr_max))
                if c[0] >= args.residual_min_area]
            residual_log["sweep_source"] = {
                "offset": "%d,%d" % (sdx, sdy),
                "boxes": ["%d,%d,%d,%d" % b for b in src_boxes],
                "rule_hits": [{"area": a, "bbox": list(b)} for a, b, _ in dirty],
            }
            print("  sweep source offset %+d,%+d -- rule hits in the source: "
                  "%d component(s)" % (sdx, sdy, len(dirty)))
            if dirty:
                for area, bbox, _ in dirty:
                    print("     SOURCE HIT  area %5d px  bbox %s" % (area, bbox))
                raise SystemExit(
                    "!! THE SOURCE LAW: the sweep source at %+d,%+d itself "
                    "satisfies the object rule in %d place(s), so sweeping would "
                    "patch a blade with pixels that read as a blade -- the "
                    "residual does not shrink, it moves. Pick a --sweep-offset "
                    "whose background is clean under this rule." % (sdx, sdy, len(dirty)))

        passes = args.sweep_passes if args.sweep else 1
        for p in range(passes):
            found = object_pixels(out, check_regions, protect,
                                  args.object_dark, args.object_bright,
                                  args.object_gmr_min, args.object_gmr_max)
            comps = [c for c in components(found)
                     if c[0] >= args.residual_min_area]
            total = sum(c[0] for c in comps)
            print("  pass %d: %d residual px in %d component(s) >= %d px%s"
                  % (p, total, len(comps), args.residual_min_area,
                     "" if comps else "  -- CLEAR"))
            for area, bbox, _ in comps:
                print("     residual  area %5d px  bbox %s" % (area, bbox))
            residual_log["passes"].append({
                "pass": p,
                "components": [{"area": a, "bbox": list(b)} for a, b, _ in comps],
                "total_px": total,
            })
            if not comps:
                break
            if not args.sweep:
                break
            dx, dy = sdx, sdy
            m = silhouette_mask((W, H), [c[2] for c in comps],
                                args.sweep_grow, args.feather, protect)
            need = m.getbbox()
            if need is None:
                break
            if args.fill == "diffuse":
                hard = silhouette_mask((W, H), [c[2] for c in comps],
                                       args.sweep_grow, 0, protect)
                patch = diffuse_fill(out, hard, args.fill_iters, args.fill_radius)
            else:
                if not (0 <= need[0] - dx and need[2] - dx <= W
                        and 0 <= need[1] - dy and need[3] - dy <= H):
                    raise SystemExit(
                        "!! sweep pass %d: source-offset %+d,%+d reads outside the "
                        "frame for bbox %s" % (p, dx, dy, need))
                patch = Image.new("RGB", (W, H))
                patch.paste(src, (dx, dy))
            out = Image.composite(patch, out, m)
            union = Image.composite(Image.new("L", (W, H), 255), union, m)
            print("     swept %d component(s) fitted to their own silhouette "
                  "(grow %d, feather %d) <- %s"
                  % (len(comps), args.sweep_grow, args.feather,
                     "DIFFUSE FILL" if args.fill == "diffuse"
                     else "background from %+d,%+d" % (dx, dy)))

        final = object_pixels(out, check_regions, protect,
                              args.object_dark, args.object_bright,
                              args.object_gmr_min, args.object_gmr_max)
        left = [c for c in components(final) if c[0] >= args.residual_min_area]
        residual_log["final"] = {
            "components": [{"area": a, "bbox": list(b)} for a, b, _ in left],
            "total_px": sum(c[0] for c in left),
        }
        print("  FINAL: %d residual px in %d component(s) >= %d px"
              % (sum(c[0] for c in left), len(left), args.residual_min_area))
        if left and args.assert_clear:
            for area, bbox, _ in left:
                print("     STILL THERE  area %5d px  bbox %s" % (area, bbox))
            raise SystemExit(
                "!! ASSERT-CLEAR FAILED: %d residual component(s) >= %d px "
                "survive inside the removal footprint. The bar's counting rules "
                "would score an identifiable partly-occluded blade as a THIRD "
                "BLADE, so nothing is written. Widen --remove, raise "
                "--sweep-passes, or re-derive the object rule on this plate."
                % (len(left), args.residual_min_area))

    for spec in args.mask_add:
        cx, cy, rx, ry, ang = parse_ellipse(spec)
        m = ellipse_mask((W, H), cx, cy, rx, ry, ang, args.feather)
        union = Image.composite(Image.new("L", (W, H), 255), union, m)
        print("mask-add    ellipse cx=%d cy=%d rx=%d ry=%d ang=%.1f -- blend mask "
              "only, no pixel patched (keeps merge/split reachable)"
              % (cx, cy, rx, ry, ang))

    if args.mask_grow > 0:
        union = union.filter(ImageFilter.MaxFilter(3))
        union = union.filter(ImageFilter.GaussianBlur(args.mask_grow))
        union = union.point(lambda v: 255 if v > 24 else 0)

    if args.dry_run:
        print("\nDRY RUN -- nothing written. %d region(s) planned." % len(regions))
        print("next step would be a LOW-strength blend over --mask-png, e.g.")
        print("  python3 pipeline/inpaint_fruit.py --init %s \\\n"
              "      --init-sha256 <sha of the composite> --mask-png %s \\\n"
              "      --strength 0.30 ..." % (args.out, args.mask_out or "<mask>"))
        return 0

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    out.save(args.out)
    out_sha = sha256_of(args.out)
    if out_sha == init_sha:
        raise SystemExit(
            "!! the composite is byte-identical to the init -- nothing was "
            "patched. Refusing to report a no-op as a fix.")
    print("\nwrote       %s" % args.out)
    print("out sha256  %s" % out_sha)

    if args.mask_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.mask_out)) or ".",
                    exist_ok=True)
        union.save(args.mask_out)
        print("wrote mask  %s (bbox %s)" % (args.mask_out, union.getbbox()))

    sidecar = os.path.splitext(args.out)[0] + ".composite.json"
    with open(sidecar, "w", encoding="utf-8") as fh:
        json.dump({
            "tool": "pipeline/leaf_count_composite.py",
            "purpose": "leaf COUNT fixed by construction before any sampler runs",
            "init": args.init,
            "init_sha256": init_sha,
            "out": args.out,
            "out_sha256": out_sha,
            "mask_out": args.mask_out,
            "remove": args.remove,
            "source_offset": args.source_offset,
            "feather": args.feather,
            "mask_grow": args.mask_grow,
            "mask_add": args.mask_add,
            "fill": args.fill,
            "fill_iters": args.fill_iters,
            "fill_radius": args.fill_radius,
            "remove_auto": args.remove_auto,
            "remove_auto_detail": auto_log,
            "residual_check": residual_log,
            "sweep": {
                "enabled": bool(args.sweep),
                "grow": args.sweep_grow,
                "passes_allowed": args.sweep_passes,
                "assert_clear": bool(args.assert_clear),
            },
            "cost_usd": 0.0,
            "model": "none -- plain PIL, no sampler, no network",
            "note": args.note,
            "sources": [
                "arXiv:2503.06884 -- prompt refinement does not improve counting",
                "arXiv:2406.10210 (Make It Count, CVPR 2025) -- plain SDXL "
                "numerals score 26-28%; count is a layout problem",
            ],
        }, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote        %s" % sidecar)
    print("\nCOUNT IS NOW STRUCTURAL, NOT PROMPTED. Verify by eye before any "
          "GPU step -- this is the sample.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
