#!/usr/bin/env python3
"""Aspect-correct conditioning plates for image-to-video.

THE DEFECT THIS EXISTS FOR (found 2026-08-08, hash-verified). Every canon still
in the tree is 832x1216 — aspect 0.684. Every video render targets 704x1280 —
aspect 0.550. Both renderers took the difference by pulling the picture:

    wan_i2v.py:541  img = Image.open(job["init"]).resize((w, h), LANCZOS)
    wan_i2v.py:713  img = Image.open(a.init).resize((w, h), LANCZOS)
    ltx_i2v.py      hands the raw PIL image to the pipe, whose preprocessor
                    resizes to height/width with the same indifference

0.684 / 0.550 = 1.2440, so every clip rendered from an approved still was 24.4%
taller than the composition the founder approved. Faces narrow, the sapling
stretches, and nothing in the log says so — a resize that changes the aspect
ratio raises nothing and looks like a resize that does not.

THE POLICY IS NOT A NEW ONE AND WAS NOT INVENTED HERE. `render_t3.py` has fitted
every delivered episode to 9:16 the same way since T3 existed, twice, in the
filter graph that produced the cuts the founder has actually screened:

    scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280

That is scale-to-COVER plus a centre crop: enlarge until both dimensions reach
the target, then take the middle. Nothing is squeezed and nothing is letterboxed;
what does not fit is cut off the long axis, evenly from both ends. This module is
that same policy expressed on a single frame, so that the plate a video model is
conditioned on is framed exactly like the episode the plate will end up inside.

The alternatives were considered and are worse HERE, whatever their merits
elsewhere. Letterboxing (`force_original_aspect_ratio=decrease` + pad, which
`hold_still.py`'s --frozen path uses) hands a diffusion model two black bars and
invites it to animate them — and render_t3 would then crop-to-cover the result
anyway, so the bars would be zoomed into the frame. Stretching is the defect.
Outpainting invents content nobody drew, which is the whole objection in
`hold_still.py`'s docstring.

WHAT 832x1216 -> 704x1280 COSTS, exactly, because "crop" should never be a vague
word in a provenance record: the kept window is 669x1216, so 163 columns leave
the frame — 81 from the left, 82 from the right, 19.6% of the width. Compositions
whose subject sits hard against a side edge will lose it, and that is a thing to
see on a plate contact sheet rather than to discover in a clip.

Pure functions on top, PIL only where pixels are actually touched, so the crop
arithmetic is unit-testable without an image and importable from the render venv.
"""

import hashlib
from pathlib import Path, PurePath

REPO = Path(__file__).resolve().parent.parent

# The name of the policy, written into every sidecar so a reader can tell which
# framing rule produced a plate without re-deriving it from the numbers.
CROP_POLICY = "cover-centre"

# HOW CLOSE COUNTS AS ALREADY-CORRECT. One pixel of width at 704x1280 moves the
# aspect by 0.00078, so anything under ~2px of disagreement is rounding in
# somebody else's resampler rather than a framing decision, and cropping it would
# throw away a row or column for nothing. Wide enough to absorb that, far too
# narrow to absorb 0.684 vs 0.550 (a difference of 0.134, sixty-seven times this).
ASPECT_EPS = 0.002


def parse_size(size) -> tuple:
    """'704x1280' -> (704, 1280). Accepts a tuple/list unchanged.

    The queue, both renderers and the sidecar all speak the WxH string, so the
    one place it becomes numbers is here rather than at four call sites with
    four slightly different splits.
    """
    if isinstance(size, (tuple, list)):
        w, h = size
    else:
        w, h = str(size).lower().split("x")
    w, h = int(w), int(h)
    if w <= 0 or h <= 0:
        raise ValueError(f"bad target size {size!r}")
    return w, h


def cover_crop_box(sw: int, sh: int, tw: int, th: int, eps: float = ASPECT_EPS):
    """The source-pixel window a cover-crop to `tw x th` keeps. PURE — unit-tested.

    Returns `(left, top, right, bottom)` in SOURCE coordinates, or None when the
    source is already on-aspect within `eps` and nothing should be cut.

    Which axis loses pixels follows from which way the aspects disagree, and both
    directions are live in this repo: a 832x1216 still into a 704x1280 clip is
    WIDER than its target and loses width, while the same still is NARROWER than
    a 1280x720 landscape target and would lose height. Getting the branch backwards
    is not a crash — it is a differently-wrong crop — so both are tested.

    The kept window is centred, and an odd remainder goes to the FAR side (the
    floor division puts the extra pixel at right/bottom). That matches ffmpeg's
    `crop=w:h` default offset of `(in_w-out_w)/2` with integer truncation, which is
    what render_t3 has been doing to delivered footage all along.
    """
    if sw <= 0 or sh <= 0:
        raise ValueError(f"bad source size {sw}x{sh}")
    src_a, tgt_a = sw / sh, tw / th
    if abs(src_a - tgt_a) <= eps:
        return None
    if src_a > tgt_a:                       # too wide -> take a column out of it
        cw = int(sh * tw / th + 0.5)
        cw = min(cw, sw)
        left = (sw - cw) // 2
        return (left, 0, left + cw, sh)
    ch = int(sw * th / tw + 0.5)            # too tall -> take a band out of it
    ch = min(ch, sh)
    top = (sh - ch) // 2
    return (0, top, sw, top + ch)


def crop_note(sw: int, sh: int, tw: int, th: int, eps: float = ASPECT_EPS) -> str:
    """One ASCII line saying exactly what the policy did. PURE — unit-tested.

    ASCII ON PURPOSE — no arrows, no em-dashes, no ellipsis. This string is
    printed by wan_i2v through a Windows cp1252 console (the encoding that has
    already killed one 25-minute render mid-success-message) and written into a
    yaml sidecar that four readers parse. It says the numbers because "cropped"
    on its own does not let anyone check the work.
    """
    box = cover_crop_box(sw, sh, tw, th, eps)
    head = f"{CROP_POLICY} (render_t3 policy: scale to cover, then centre crop)"
    if box is None:
        return (f"{head}: {sw}x{sh} is already within {eps} of the {tw}x{th} "
                f"aspect, no crop, LANCZOS to {tw}x{th}")
    left, top, right, bottom = box
    if right - left < sw:
        cut = sw - (right - left)
        where = f"{left} left, {sw - right} right"
        axis = f"{cut}px of width ({where})"
    else:
        cut = sh - (bottom - top)
        where = f"{top} top, {sh - bottom} bottom"
        axis = f"{cut}px of height ({where})"
    pct = 100.0 * cut / (sw if right - left < sw else sh)
    return (f"{head}: {sw}x{sh}, cropped {axis} = {pct:.1f}%, kept "
            f"{right - left}x{bottom - top}, LANCZOS to {tw}x{th}")


def sha256_file(path) -> str:
    """The bytes on disk, not a summary of them. Cheap at plate sizes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def posix(path) -> str:
    """Spell `path` with forward slashes whatever platform is holding it. PURE.

    A sidecar is written on one machine and read on another. Until 2026-08-08 the
    two v2 clips rendered on the 5090 box recorded
    `path: genomes\\sapling\\nodes\\...` — a live pointer on Windows and a dead
    one on the Mac where sidecars are actually consumed, because a backslash is a
    legal filename character on posix, so nothing raises: the path simply names a
    file that does not exist. Repo-relative provenance is only portable if its
    separator is too.

    The flavour of an already-constructed PurePath is PRESERVED rather than
    re-parsed, which is what makes this testable off Windows: re-wrapping a
    WindowsPath in the local Path flavour would fold `a\\b` into one segment and
    the conversion would silently become a no-op on the machine running the test.
    """
    return (path if isinstance(path, PurePath) else PurePath(path)).as_posix()


def rel_to_repo(path) -> str:
    """Repo-relative if it lives in the tree, absolute otherwise.

    A sidecar naming `genomes/sapling/.../01-the-keyboard.png` is a pointer
    anybody can follow on any machine; one naming `C:/banyan-video/...` is a
    pointer to a folder that is deleted on purpose.
    """
    p = Path(path)
    try:
        return posix(p.resolve().relative_to(REPO))
    except (ValueError, OSError):
        return posix(p)


def fit_cover(img, tw: int, th: int, eps: float = ASPECT_EPS) -> tuple:
    """Crop-to-cover then resample one PIL image to exactly `tw x th`.

    Returns `(fitted_image, info)`. `info` carries `box` (None when no crop was
    needed), `source_wxh`, `plate_wxh`, `crop_px` and the `crop_note` line, so a
    caller can log it and a sidecar can record it without recomputing anything.

    The final resize is unconditional and is a no-op only by coincidence: after
    the crop the aspect is right but the SCALE usually is not, and 669x1216 into
    a model that was asked for 704x1280 is the same class of silent wrongness
    this module exists to end.
    """
    from PIL import Image

    sw, sh = img.size
    box = cover_crop_box(sw, sh, tw, th, eps)
    out = img.crop(box) if box else img
    if out.size != (tw, th):
        out = out.resize((tw, th), Image.LANCZOS)
    kept = (box[2] - box[0], box[3] - box[1]) if box else (sw, sh)
    return out, {
        "box": box,
        "source_wxh": f"{sw}x{sh}",
        "plate_wxh": f"{tw}x{th}",
        "kept_wxh": f"{kept[0]}x{kept[1]}",
        "crop_px": (sw - kept[0]) + (sh - kept[1]),
        "crop_note": crop_note(sw, sh, tw, th, eps),
    }


def prepare_plate(src, size, out_dir, tag: str = "") -> tuple:
    """Write the conditioning plate for `src` at `size`; return (path, record).

    `record` is the `init_frame:` block a sidecar publishes. It names BOTH files
    on purpose. The source still is the durable half — it is in the repo, it is
    what the founder approved, and its sha is what proves which revision of a
    twice-redrawn still was used. The plate is the half the model actually saw,
    and it lives in a scratch dir that gets deleted, so recording only its path
    would leave a record pointing at nothing within the week.

    Written as PNG beside the job rather than into a temp file: when a clip comes
    back wrong the first question is what went in, and the answer should be a file
    someone can open, not a re-run of the crop arithmetic.
    """
    from PIL import Image

    tw, th = parse_size(size)
    src = Path(src)
    with Image.open(src) as raw:
        img = raw.convert("RGB")
    fitted, info = fit_cover(img, tw, th)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{tag + '-' if tag else ''}{tw}x{th}.png"
    fitted.save(out)
    return out, {
        "path": rel_to_repo(src),
        "sha256": sha256_file(src),
        "source_wxh": info["source_wxh"],
        "plate_wxh": info["plate_wxh"],
        "crop_policy": info["crop_note"],
        "plate_path": str(out),
        "plate_sha256": sha256_file(out),
    }
