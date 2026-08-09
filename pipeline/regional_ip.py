#!/usr/bin/env python3
"""Region geometry for masked IP-Adapter renders — memo §3.3.

`pipeline/research/two-subject-composition.md` §3.3 selects regional IP-Adapter
for the goblin-identity defect (P2): route IMAGE conditioning to the character's
region only, and leave the plant region to the r6 vocabulary prompt, which
already scores 4/4 on the plant predicates and must not be disturbed.

Everything here is pure geometry over PIL — no torch, no diffusers, no network —
so the half of the recipe that decides WHERE conditioning lands is testable in CI
beside the rest of the pipeline. `render_b13r7.py` supplies the model half.

Boxes are `(x0, y0, x1, y1)` in normalised 0..1 frame coordinates, origin top
left, so one box describes the same region at any render size.
"""

from __future__ import annotations

Box = tuple


def parse_box(text: str) -> Box:
    """`"x0,y0,x1,y1"` → a validated normalised box."""
    parts = [p.strip() for p in str(text).split(",")]
    if len(parts) != 4:
        raise ValueError(f"box needs 4 comma-separated numbers, got {len(parts)}: {text!r}")
    try:
        nums = tuple(float(p) for p in parts)
    except ValueError as exc:
        raise ValueError(f"box has a non-numeric edge: {text!r}") from exc
    return validate_box(nums)


def validate_box(box) -> Box:
    """Reject anything that is not a real region inside the frame."""
    if len(tuple(box)) != 4:
        raise ValueError(f"box needs 4 edges, got {len(tuple(box))}")
    x0, y0, x1, y1 = (float(v) for v in box)
    for name, v in (("x0", x0), ("y0", y0), ("x1", x1), ("y1", y1)):
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"box edge {name}={v} is outside 0..1")
    if x0 >= x1 or y0 >= y1:
        raise ValueError(f"box is empty or inverted: {(x0, y0, x1, y1)}")
    return (x0, y0, x1, y1)


def box_to_pixels(box, width: int, height: int) -> Box:
    """Normalised box → integer pixel box, clamped and never empty.

    Rounding a thin box could collapse it to zero pixels and silently condition
    nothing, so the result is widened to at least one pixel per axis.
    """
    x0, y0, x1, y1 = validate_box(box)
    if width <= 0 or height <= 0:
        raise ValueError(f"frame must be positive, got {width}x{height}")
    px0 = max(0, min(width - 1, round(x0 * width)))
    py0 = max(0, min(height - 1, round(y0 * height)))
    px1 = max(px0 + 1, min(width, round(x1 * width)))
    py1 = max(py0 + 1, min(height, round(y1 * height)))
    return (px0, py0, px1, py1)


def coverage(box) -> float:
    """Fraction of the frame the box covers."""
    x0, y0, x1, y1 = validate_box(box)
    return (x1 - x0) * (y1 - y0)


def side_bands(box) -> Box:
    """Unmasked margins as `(left, right, top, bottom)` fractions.

    The plant lives in these margins, so the driver asserts on them: a box with
    no margin left is a whole-frame IP-Adapter wearing a mask's name.
    """
    x0, y0, x1, y1 = validate_box(box)
    return (x0, 1.0 - x1, y0, 1.0 - y1)


def region_mask(width: int, height: int, box, feather: int = 0):
    """A greyscale mask for `IPAdapterMaskProcessor`: white = condition here.

    `feather` blurs the edge by that many pixels. The box edge cuts through the
    character's own silhouette — the reference goblin's ear tips sit within a
    few percent of it — and a hard step there conditions the ear at full
    strength and its tip at none, so the default softens it.
    """
    from PIL import Image, ImageDraw, ImageFilter

    if int(feather) < 0:
        raise ValueError(f"feather must be >= 0, got {feather}")
    px0, py0, px1, py1 = box_to_pixels(box, width, height)
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rectangle((px0, py0, px1 - 1, py1 - 1), fill=255)
    if int(feather):
        mask = mask.filter(ImageFilter.GaussianBlur(radius=int(feather)))
    return mask


def crop_reference(image, box):
    """Crop an IP-Adapter reference to its subject.

    CLIP encodes the whole reference, so an uncropped frame would carry that
    frame's grass, shade and seedlings into the character's region — the r6
    reference contains three seedlings of its own. Cropping to the subject is
    what makes the conditioning about the character.
    """
    px0, py0, px1, py1 = box_to_pixels(box, image.width, image.height)
    return image.crop((px0, py0, px1, py1))


def describe(box) -> str:
    """One-line box summary for logs and sidecars."""
    x0, y0, x1, y1 = validate_box(box)
    left, right, top, bottom = side_bands(box)
    return (f"x {x0:.2f}-{x1:.2f}, y {y0:.2f}-{y1:.2f} "
            f"({coverage(box) * 100:.0f}% of frame; free margins "
            f"L{left * 100:.0f}% R{right * 100:.0f}% "
            f"T{top * 100:.0f}% B{bottom * 100:.0f}%)")
