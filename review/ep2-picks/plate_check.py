#!/usr/bin/env python3
"""Refuse to fire a motion wave whose starting picture is not a scene.

On 2026-08-14 nineteen motion renders went out and six of them animated a
CHARACTER REFERENCE CARD -- one figure standing on a blank pale ground, no
location, no other character -- because the wave's source map sent each beat to
"its newest good job" and for the guards that job was the identity pick. Two of
those six scored near the top of the wave on frame-difference, so nothing
downstream caught it; a card breathing measures exactly like a shot. The law out
of it was LOOK AT THE INIT, NOT THE JOB IT CAME FROM, and a law that lives in a
ledger gets obeyed until the night someone is in a hurry. This is the same law
as code.

HOW IT DECIDES. It cover-crops each job's --src exactly as the box will, then
measures the OUTER 8% BAND of the result: what fraction of those border pixels
sit within +/-8 luminance levels of the border's own median. A drawn place --
grass, sky, a field, a room -- has texture out to its edges. A reference card is
flat paper behind a centred figure.

The threshold is measured, not guessed. Against the seventeen inits of that wave
plus beat 21's night plate, labelled by eye:

    scenes    0.016 .. 0.350, then 0.489   (the 0.489 is beat 21)
    cards     0.750 .. 0.968                (b10 b06 b11 b07 b05 b09)

so FLAT_MAX sits at 0.62, the middle of the real gap. Note where the margin
actually is: it is NOT the 0.40 the bulk of the scenes suggest. Beat 21's plate --
a night field, mostly dark sky -- reads 0.489, because a nearly empty night shot
genuinely is close to flat. That is the tightest legitimate case known, and any
future night or fog plate will sit near it.

The luminance is autocontrast-normalised first, which is what buys that margin:
without it beat 21 reads 0.547 and clears the old 0.55 threshold by three
thousandths, while the cards do not move at all because they already span the
full range. Border standard deviation was tried first and REJECTED outright -- it
does not separate the two groups even a little, card b09 reads 33.0 against scene
b13's 44.0. Flatness is about how much of the border is ONE colour, which is what
"blank" actually means; spread is not.

TWO THINGS IT REFUSES ON, and it exits nonzero for both, because a check that
prints a problem and returns 0 is a check that gets chained with ';' and ignored
-- which is how the publish-collision bug shipped a fourth time.

  * a plate that measures as a card
  * a plate it could not fetch and therefore did not measure

The second is deliberate. "I could not check" must never read as "fine". Both are
overridable per job, never globally, so the override names what is being waived:

    plate_check.py pipeline/jobs/ep2-b*-nw-0815.yaml && box_enqueue.py ...
    plate_check.py --ack-card ep2-b18-figloop-0815 <yamls>      # a macro close-up
    plate_check.py --ack-unfetchable ep2-b12-leaf-0815 <yamls>  # a plates-local src

It always writes a contact sheet of every plate in the batch, pass or fail, so
the three-minute look that would have stopped six of nineteen is a file on disk
rather than a good intention.

ONLY MOTION JOBS ARE CHECKED, and that scoping is the point rather than a
convenience. A figure on blank paper is the CORRECT output for the stills lane's
identity work -- charref sheets, costume picks, turnarounds all want exactly the
picture this refuses. What is wrong is feeding one to an i2v render. So a job is
checked when its steps run ltx_i2v and skipped otherwise, which is what makes it
safe to chain in front of a shared queue without blocking another lane.
"""
import argparse
import io
import statistics
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageOps

REPO = Path(__file__).resolve().parents[2]
BRANCH = "origin/farm-results-rtx5090"
BOX_PREFIX = "c:\\banyan-farm\\courier-box\\farm-out\\"

FLAT_MAX = 0.62        # midpoint of the 0.489 -> 0.750 gap; see the docstring
BAND = 0.08            # outer fraction of the short side sampled as "border"
TOL = 8                # luminance levels either side of the border median
SIZE = (704, 1280)     # what the box crops to, so we measure what the model sees


def branch_path(src: str):
    """The results-branch path for a box --src, or None if it is not from there."""
    s = src.replace("/", "\\")
    low = s.lower()
    if low.startswith(BOX_PREFIX):
        return "farm-out/" + s[len(BOX_PREFIX):].replace("\\", "/")
    return None


def fetch(path: str):
    out = subprocess.run(["git", "show", f"{BRANCH}:{path}"], cwd=REPO, capture_output=True)
    if out.returncode != 0 or not out.stdout:
        return None
    return out.stdout


def cover_crop(im: Image.Image) -> Image.Image:
    """The box's cover_crop.py, so the number describes the real conditioning image."""
    W, H = SIZE
    sw, sh = im.size
    scale = max(W / float(sw), H / float(sh))
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - W) // 2, (nh - H) // 2
    return im.crop((left, top, left + W, top + H))


def flatness(im: Image.Image) -> float:
    """Fraction of the outer band within TOL levels of that band's median."""
    g = ImageOps.autocontrast(im.convert("L"), cutoff=1)
    w, h = g.size
    band = max(2, int(min(w, h) * BAND))
    px = g.load()
    vals = []
    for y in range(0, h, 2):                       # every other row/col: same
        for x in range(0, w, 2):                   # answer, a quarter of the work
            if x < band or x >= w - band or y < band or y >= h - band:
                vals.append(px[x, y])
    med = statistics.median(vals)
    return sum(1 for v in vals if abs(v - med) <= TOL) / len(vals)


def is_motion(spec: dict) -> bool:
    """True when this job actually animates. Read off argv, not the job id.

    Ids drift into nicknames; the argv is what runs. This is the same reasoning
    box_job_minutes.py uses to classify a job by kind.
    """
    blob = " ".join(" ".join(s.get("argv") or []) for s in spec.get("steps") or [])
    return "ltx_i2v" in blob


def crop_src(spec: dict):
    for s in spec.get("steps") or []:
        argv = s.get("argv") or []
        if "--src" in argv:
            return argv[argv.index("--src") + 1]
    return None


def contact_sheet(shots: list, out: Path, cols: int = 6, tw: int = 150):
    """Every plate in the batch on one page, red-bordered where it failed."""
    if not shots:
        return
    th = int(tw * SIZE[1] / SIZE[0])
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 6) + 6, rows * (th + 6) + 6), (255, 255, 255))
    for i, (_, im, bad) in enumerate(shots):
        t = im.resize((tw, th), Image.LANCZOS)
        if bad:                                    # 3px red edge, drawn by hand
            t = t.convert("RGB")
            p = t.load()
            for x in range(tw):
                for d in range(3):
                    p[x, d] = p[x, th - 1 - d] = (220, 60, 60)
            for y in range(th):
                for d in range(3):
                    p[d, y] = p[tw - 1 - d, y] = (220, 60, 60)
        sheet.paste(t, (6 + (i % cols) * (tw + 6), 6 + (i // cols) * (th + 6)))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jobs", nargs="+")
    ap.add_argument("--ack-card", action="append", default=[],
                    help="job id whose flat plate is deliberate (a macro, a close-up)")
    ap.add_argument("--ack-unfetchable", action="append", default=[],
                    help="job id whose plate is not on the results branch")
    ap.add_argument("--sheet", default="review/ep2-picks/plate-check-sheet.png")
    a = ap.parse_args()

    shots, refusals, notes = [], [], []
    for f in a.jobs:
        spec = yaml.safe_load(Path(f).read_text(encoding="utf-8"))
        jid = str(spec.get("id") or Path(f).stem)
        if not is_motion(spec):
            notes.append(f"  {jid}: not a motion job, skipped -- a blank ground is "
                         f"correct for identity work")
            continue
        src = crop_src(spec)
        if not src:
            notes.append(f"  {jid}: no crop step, nothing to check")
            continue
        bp = branch_path(src)
        blob = fetch(bp) if bp else None
        if blob is None:
            where = bp or src
            if jid in a.ack_unfetchable:
                notes.append(f"  {jid}: plate not fetchable, WAIVED -- {where}")
            else:
                refusals.append(f"  {jid}: could not fetch its plate, so it was NOT checked\n"
                                f"      {where}\n"
                                f"      waive with --ack-unfetchable {jid} if that is intended")
            continue
        im = cover_crop(Image.open(io.BytesIO(blob)))
        flat = flatness(im)
        bad = flat >= FLAT_MAX
        shots.append((jid, im, bad and jid not in a.ack_card))
        mark = "CARD" if bad else "scene"
        if bad and jid in a.ack_card:
            notes.append(f"  {jid}: flatness {flat:.3f} {mark}, WAIVED")
        elif bad:
            refusals.append(f"  {jid}: flatness {flat:.3f} -- this plate is a blank-background\n"
                            f"      card, not a place. Cards measure like shots once animated.\n"
                            f"      {bp}\n"
                            f"      waive with --ack-card {jid} if it is a deliberate close-up")
        else:
            notes.append(f"  {jid}: flatness {flat:.3f} {mark}")

    sheet = REPO / a.sheet
    contact_sheet(shots, sheet)
    for n in notes:
        print(n)
    if shots:
        print(f"\ncontact sheet: {sheet.relative_to(REPO)}  ({len(shots)} plate(s))")
    if refusals:
        print(f"\n!! REFUSING to pass {len(refusals)} of {len(a.jobs)} job(s):\n")
        print("\n".join(refusals))
        return 1
    # Say what was actually measured. "OK" over a batch that was entirely
    # skipped would be the same lie this whole tool exists to stop.
    if shots:
        print(f"\nplate check OK: {len(shots)} plate(s) measured, every one a scene"
              + (f"; {len(a.jobs) - len(shots)} job(s) not checked" if len(shots) != len(a.jobs) else ""))
    else:
        print(f"\nplate check: NOTHING MEASURED -- none of the {len(a.jobs)} job(s) animate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
