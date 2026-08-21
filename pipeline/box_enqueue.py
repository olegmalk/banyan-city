#!/usr/bin/env python3
"""Put a job into the box-resident queue, from here, safely.

The queue itself is just directories on the card (`box_runner.py` drains them),
so enqueueing is "write a json into ready/". Doing that by hand is how you get
the three failures this script exists to prevent:

  1. A job naming an unapproved node. That is not a failed job, it is a dead
     daemon -- the §6 gate raises SystemExit, which `except Exception` does not
     catch (farm_worker.py:517). So `--check-approval` runs first, against the
     leaf the gate actually reads, and refuses to enqueue.
  2. A reused id. MAX_ATTEMPTS keys on id, so a re-queued id inherits its
     predecessor's spent attempts and can be retired without ever running. Ids
     are stamped with an epoch second unless one is given explicitly.
  3. A half-written job file being claimed mid-copy. The runner claims by
     renaming out of ready/, and scp writes in place -- so the file lands in a
     staging dir and is MOVED into ready/ as the last step.
  4. Two queued jobs whose `payload:` blocks name the SAME box paths. Payloads
     are written at ENQUEUE time, so the second enqueue overwrites the first
     job's prompt before either job runs, and the box renders the second job's
     picture under both names. On 2026-08-13 ep2-b01-shape and its twin did
     exactly that, five seconds apart, into one parent-named directory; only the
     declared-artifact check noticed. See reserve_payload/payload_collisions.
  5. A motion job whose starting picture is a CHARACTER CARD rather than a
     scene. On 2026-08-14 nineteen renders went out and six animated a costume
     identity sheet -- one figure on blank pale paper, no location -- because the
     wave pointed each beat at "its newest good job". Two of the six scored at
     the TOP of the wave on frame-difference, so nothing downstream caught it: a
     card breathing measures exactly like a shot. See plate_problems.
  6. The same wave, caught a second way. The border statistic and "is a place
     depicted" have come apart -- the classes interleave, a tight portrait card
     reads 0.236 and a legitimate night field reads 0.489 -- so the picture
     alone cannot carry the check. The reference SET that drew the plate does
     split cleanly, and a motion job's --src names the job that produced it. See
     refs_problems. Neither guard replaces the other: refs is exact but is a
     denylist, flatness is fuzzy but sees blank paper from any source.

     THEY ARE NOT INDEPENDENT CONFIRMATIONS OF EACH OTHER, and until 2026-08-16
     this file said they were ("two independent readings of the same failure").
     CARD_REFS_DENYLIST was CHOSEN by scoring every plate on the results branch
     with border_flatness and keeping the sets whose plates scored >=0.62 -- the
     table under refs_problems is that thresholding, written down. So when both
     fire on one job you are reading ONE measurement twice, not two witnesses
     agreeing, and the second refusal adds no evidence the first did not have.
     Both still run: a refs refusal names a fact a lane can act on (re-cut from
     another set) and reaches plates the picture check misses. But the output
     now says plainly when the two are the same signal.

    python3 pipeline/box_enqueue.py pipeline/jobs/<spec>.yaml [--dry-run]
    python3 pipeline/box_enqueue.py --list        # what is queued right now

  7. A card that runs dry the moment every lane is mid-thought. On 2026-08-15
     the GPU idled four separate times and three sessions died on usage limits
     with work un-queued. `--backlog` files a spec into `backlog/` instead of
     `ready/`, through every guard above, where box_autofill.py picks it up when
     the queue falls under its floor of MINUTES -- with no session alive. The
     one thing that door refuses and this one does not is a `plate_ack:` waiver;
     see backlog_problems.

    python3 pipeline/box_enqueue.py pipeline/jobs/<spec>.yaml --backlog

  8. A job the card has ALREADY RUN, re-filed by a lane that did not look in
     done/ first. Every guard above compares against LIVE work only, so a
     finished job owned nothing and a re-file walked straight in: 264s of GPU
     on 2026-08-19 answering a question already answered, and three finished
     jobs re-filed clean on 2026-08-20 with one of them re-rendered. Refused
     now by content rather than by name -- same steps and same payload is a
     duplicate, a changed spec is a revision and still passes. See the note
     above duplicate_problems for why those two answers differ.

    python3 pipeline/box_enqueue.py pipeline/jobs/<spec>.yaml --again
"""

from __future__ import annotations

import argparse
import json
import ntpath
import os
import re
import subprocess
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSH_HOST = "rtx5090"
QUEUE_ROOT = r"C:\banyan-queue"
STAGING = QUEUE_ROOT + r"\incoming"
NODES = os.path.join(REPO, "genomes", "sapling", "nodes")

# Where this machine remembers which box payload paths it has handed out. The
# box cannot answer the question itself: `to_job` deliberately does not copy
# `payload:` into the job json, so a queued job on the card carries no record of
# the files it was given. Local, gitignored, append-only -- see reserve_payload.
PAYLOAD_INDEX = os.path.join(REPO, "pipeline", ".box-payload-index.jsonl")

# How long a reservation counts as live on its own, before the box queue is the
# only thing keeping it alive. It has to outlast the gap between reserving a
# path and the job appearing in ready/ -- an scp of five payload files plus a
# move, seconds -- because that gap is precisely when the twin slipped in.
RESERVE_GRACE_SEC = 120


def ssh(command: str, timeout: int = 90):
    # encoding named on purpose: text mode alone decodes with the locale codec,
    # and cmd.exe answers in cp1252 while our prompts carry ellipses and Chinese
    # negatives. The decode happens on subprocess's reader thread, where the
    # error never reaches us -- stdout just silently becomes None.
    return subprocess.run(["ssh", "-o", "ConnectTimeout=25", "-o", "BatchMode=yes",
                           SSH_HOST, command],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)


def newest_t0_leaf(node: str):
    leaves = os.path.join(NODES, node, "leaves")
    if not os.path.isdir(leaves):
        return None
    names = sorted(n for n in os.listdir(leaves) if "-t0-" in n and n.endswith(".yaml"))
    return os.path.join(leaves, names[-1]) if names else None


def node_is_approved(node: str) -> tuple:
    """(approved, detail) read the same way the render gate reads it."""
    leaf = newest_t0_leaf(node)
    if not leaf:
        return False, "no *-t0-*.yaml leaf under %s" % node
    with open(leaf, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("approved_by:"):
                value = s.split(":", 1)[1].strip()
                if "#" in value and not value.startswith(("'", '"')):
                    value = value.split("#", 1)[0].strip()
                value = value.strip("'\"")
                if value.startswith("founder"):
                    return True, "%s: approved_by %s" % (os.path.basename(leaf), value)
                return False, "%s: approved_by %s" % (os.path.basename(leaf), value)
    return False, "%s: no approved_by key" % os.path.basename(leaf)


def load_spec(path: str) -> dict:
    """Read a job spec. yaml if pyyaml is here, json otherwise."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if path.endswith(".json"):
        return json.loads(text)
    try:
        import yaml
    except ImportError:
        sys.exit("!! pyyaml not available and %s is not json" % path)
    return yaml.safe_load(text)


def to_job(spec: dict, again: bool = False) -> dict:
    """Spec (repo vocabulary) -> job (what box_runner executes).

    Only the keys the runner reads are copied through. Everything else in a spec
    -- consumer, success, why, gate -- is planning metadata that stays in the
    repo file, where a person reads it, rather than riding to the box as noise.

    `again` mints a token below the epoch's resolution. Two things need it and
    the epoch alone gives neither: a re-file inside the same second, and a spec
    that opted out of stamping (`stamp_id: false`, or an id already ending in
    ten digits) where the filename would otherwise be identical -- and enqueue()
    moves with /Y, so an identical filename OVERWRITES the record instead of
    sitting beside it. An override that quietly destroys the evidence of the run
    it is overriding is worse than the refusal it bypassed.
    """
    jid = spec.get("id")
    if not jid:
        sys.exit("!! spec has no id")
    if spec.get("stamp_id", True) and not jid[-10:].isdigit():
        jid = "%s-%d" % (jid, int(time.time()))
    if again:
        jid = "%s-again%06x" % (jid, time.time_ns() % 0x1000000)
    job = {
        "id": jid,
        "task": spec.get("task", spec.get("id")),
        "node": spec.get("node"),
        "beat": spec.get("beat"),
        "worker": "box-runner",
        "priority": spec.get("priority", 100),
        "needs_gpu": bool(spec.get("needs_gpu", True)),
        "max_attempts": int(spec.get("max_attempts", 1)),
        "env": spec.get("env") or {},
        "steps": spec.get("steps") or [],
        "artifacts": spec.get("artifacts") or [],
    }
    if not job["steps"]:
        sys.exit("!! spec %s has no steps" % jid)
    for i, step in enumerate(job["steps"]):
        if not step.get("argv"):
            sys.exit("!! spec %s step %d has no argv" % (jid, i))
    return job


# --------------------------------------------------------------------------
# The plate check. Lifted, threshold and statistic unchanged, from
# review/ep2-picks/plate_check.py, which the motion-wave lane wrote and
# validated on 2026-08-14 against the wave that broke: of the nineteen `-lw`
# jobs it refuses exactly the six that animated cards and no others, and of the
# eleven jobs re-cut afterwards it passes all eleven. It lives here as well
# because a law that must be remembered before every enqueue is a law that gets
# skipped on the night someone is in a hurry.
#
# WHAT IT MEASURES. The job's --src is cover-cropped exactly as the box will
# crop it, then the OUTER 8% BAND is measured: what fraction of those border
# pixels sit within +/-8 autocontrast-normalised luminance levels of the
# border's own median. A drawn place -- grass, sky, a field, a room -- has
# texture out to its edges. A reference card is flat paper behind a figure.
#
# THE THRESHOLD IS MEASURED, NOT GUESSED, and the margin is thinner than the
# bulk of the data suggests. Labelled by eye over that wave:
#
#     scenes    0.016 .. 0.350, then 0.489      (the 0.489 is beat 21)
#     cards     0.750 .. 0.968                  (b05 b06 b07 b09 b10 b11)
#
# 0.62 is the middle of that gap. Beat 21 -- a night field, mostly dark sky --
# reads 0.489 and is the TIGHTEST LEGITIMATE CASE KNOWN: a nearly empty night
# shot genuinely is close to flat. The next fog or night plate will land near
# it, so whoever meets a refusal in the 0.5s should look at the picture rather
# than assume the guard is right. Do not retune either number without re-running
# the labelled set; they were measured off the wave that broke.
#
# BORDER STANDARD DEVIATION WAS TRIED FIRST AND REJECTED. It does not separate
# the two groups even a little -- card b09 reads 33.0 against scene b13's 44.0 --
# because a card's ground can carry a gradient and a night scene can be dim.
# Flatness asks how much of the border is ONE colour, which is what "blank"
# actually means; spread is not.
#
# WHAT IT CANNOT SEE, and this is why a PASS here is not a clearance. The
# statistic measures UNIFORMITY of the border, not whether a place is depicted,
# and on 2026-08-15 two lanes re-measured it and found the two questions have
# come apart. Everything below is a measured number on a real file, cropped
# exactly as this code crops it:
#
#   * a card whose border carries the texture passes. The same guardpick sweeps
#     that produced the six refused cards also produced tight portraits -- one
#     figure, no location, no second character, a token hedge behind and in two
#     cases a printed card border -- that read 0.236 (b06 r2-s0), 0.287
#     (b07 r2-s1), 0.052 (b09 r2-s3) and 0.056 (b10 r2-s3). A printed border is
#     texture; the statistic rewards it. None of those four was any job's --src,
#     so the wave that broke is still 6/6 refused, but a source map that had
#     picked a different seed would have walked straight through this guard.
#   * a WORLD-ABSENT frame passes by a mile. farm-out/ep2-b18-purplefig/
#     b13-init-704x1280.png -- one glossy fruit on a cream-and-mauve gradient
#     with a hard diagonal shadow, no sapling, no sky, no world -- reads 0.060.
#     A gradient with a shadow sweeping across it is SMOOTH but not UNIFORM, so
#     it measures as "textured" while containing nothing.
#
# AND NO THRESHOLD MOVE FIXES THAT, so do not retune it: beat 21's legitimate
# night field reads 0.489, ABOVE those four cards and above the fruit. The
# classes are interleaved, not merely close, and any cut point that catches
# 0.236 has already failed 0.489. What survives retuning is the shape of the
# claim: a refusal here is EVIDENCE (blank paper behind a figure, 6/6 on the
# labelled wave, zero false alarms), a pass here is only the ABSENCE of that one
# piece of evidence, and the pass line must never say more than that. A lane
# that reads "a scene" and skips opening the init is doing exactly what cost
# nineteen renders.
#
# A KNOWN FALSE POSITIVE, opened and confirmed by eye on 2026-08-16:
# farm-out/ep2-b10-patrol-scene-r2-0813/10-no-form-ipa-r0-w010-s1.png reads
# 0.740 and IS A SCENE -- a guard in a long coat holding a bark board in a mown
# field, a clipped hedge behind him, yellow flowers in the foreground grass, and
# a SECOND guard in the mid-ground. It refuses because its outer band is flat
# sky above and flat grass below, two materials at nearly the same lightness.
# It is the --src of twelve i2v specs (eight on beat 06, two on 09, two on 10),
# all of which this guard is holding.
#
# COLOUR FLATNESS WAS TRIED AS THE FIX AND REJECTED ON THE POPULATION, which is
# the part worth keeping. On the labelled wave it looked decisive: the six cards
# barely move (min 0.745) while every scene drops and this plate drops to 0.461,
# so 0.62 still sits in the gap and the threshold would not have had to move.
# Then it was swept across all 2510 pngs on the results branch. Swapping the
# statistic flips 36 plates, all of them from BLOCK to PASS and none the other
# way -- 22 distinct pictures, and a contact sheet of those 22 shows at least
# fourteen are real cards and costume turnarounds, including a two-view
# front-and-back character sheet (ep2-guard-sheet-b-r2-0814, 0.685 -> 0.608).
# The reason is plain once seen: a card on a pale COLOUR GRADIENT is flat in
# lightness and not flat in colour, so colour flatness releases exactly the
# cards whose paper is tinted. Top-vs-bottom hue split and border colour spread
# were measured too and interleave worse (cards span 0..206 on strip-median
# distance, scenes 21..186).
#
# So the statistic stays as it was and the number is REPORTED, not obeyed:
# border_colour_flatness runs on every refusal and a low value is the signature
# of a two-material border -- the case above. Nobody has found an image-only
# rule that passes that plate and still refuses a costume sheet. Do not go
# looking for one by moving PLATE_FLAT_MAX; the sweep is in
# review/ep2-picks/plate-colour-sweep-0816.tsv -- both numbers for all 2510
# plates, with the 22 flipped pictures listed and labelled by eye in its header
# -- and any candidate has to be run against it before it is believed.
#
# THE UNFETCHABLE REFUSAL IS THE PART THAT HAS NOT FAILED, and it earned its
# keep on its first outing: it caught a silently-swapped plate whose path was
# built from the new beat's directory and the old beat's filename. "I could not
# check" must keep exiting nonzero whatever happens to the border statistic.
RESULTS_BRANCH = "origin/farm-results-rtx5090"
BOX_OUT_PREFIX = "c:\\banyan-farm\\courier-box\\farm-out\\"
PLATE_FLAT_MAX = 0.62      # midpoint of the 0.489 -> 0.750 gap; see above
PLATE_BAND = 0.08          # outer fraction of the short side sampled as "border"
PLATE_TOL = 8              # luminance levels either side of the border median
PLATE_COLOUR_TOL = 6       # RGB levels either side of the border median COLOUR;
                           # diagnostic only, decides nothing -- border_colour_flatness
PLATE_SIZE = (704, 1280)   # what the box crops to, so we measure what LTX sees


def job_animates(spec: dict) -> bool:
    """True when this job actually renders motion. Read off argv, not the id.

    SCOPE IS THE POINT HERE, not a convenience. A figure on blank paper is the
    CORRECT output for the stills lane's identity work -- charref sheets,
    costume picks, turnarounds all want exactly the picture the plate check
    refuses. What is wrong is feeding one to an i2v render, so only i2v jobs are
    checked and the shared queue stays open to every other lane.

    Classified the way box_job_minutes.job_kind classifies: by the scripts the
    steps actually run. Ids are written by whoever filed the job and drift into
    nicknames (-lw, -nw, -gp, -figloop); the argv is what runs.
    """
    blob = " ".join(" ".join(s.get("argv") or []) for s in spec.get("steps") or [])
    return "ltx_i2v" in blob


def crop_src(spec: dict):
    """The picture a job conditions on: the --src its crop step reads."""
    for step in spec.get("steps") or []:
        argv = step.get("argv") or []
        if "--src" in argv:
            i = argv.index("--src")
            if i + 1 < len(argv):
                return str(argv[i + 1])
    return None


def results_branch_path(src: str):
    """The results-branch path for a box --src, or None if it is not from there.

    Only farm-out/ is fetchable from this machine. A --src under plates-local or
    any other box-only directory returns None, which is a refusal and not a
    shrug -- see plate_problems.
    """
    s = str(src).replace("/", "\\")
    if s.lower().startswith(BOX_OUT_PREFIX):
        return "farm-out/" + s[len(BOX_OUT_PREFIX):].replace("\\", "/")
    return None


def fetch_results_blob(path: str):
    """The bytes of a file on the results branch, or None. Read-only, no fetch."""
    out = subprocess.run(["git", "show", "%s:%s" % (RESULTS_BRANCH, path)],
                         cwd=REPO, capture_output=True)
    if out.returncode != 0 or not out.stdout:
        return None
    return out.stdout


def cover_crop(im):
    """The box's cover_crop.py, so the number describes the real init image."""
    from PIL import Image

    W, H = PLATE_SIZE
    sw, sh = im.size
    scale = max(W / float(sw), H / float(sh))
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - W) // 2, (nh - H) // 2
    return im.crop((left, top, left + W, top + H))


def border_flatness(im) -> float:
    """Fraction of the outer band within PLATE_TOL levels of that band's median.

    Autocontrast first, and that is what buys the margin: without it beat 21's
    night plate reads 0.547 and clears the old 0.55 threshold by three
    thousandths, while the cards do not move at all because they already span
    the full range.
    """
    import statistics

    from PIL import ImageOps

    g = ImageOps.autocontrast(im.convert("L"), cutoff=1)
    w, h = g.size
    band = max(2, int(min(w, h) * PLATE_BAND))
    px = g.load()
    vals = []
    for y in range(0, h, 2):                    # every other row/col: the same
        for x in range(0, w, 2):                # answer, a quarter of the work
            if x < band or x >= w - band or y < band or y >= h - band:
                vals.append(px[x, y])
    med = statistics.median(vals)
    return sum(1 for v in vals if abs(v - med) <= PLATE_TOL) / len(vals)


def border_colour_flatness(im) -> float:
    """The same band, asked whether it is one COLOUR rather than one BRIGHTNESS.

    Fraction of border pixels within PLATE_COLOUR_TOL of the band's median
    colour in ALL THREE channels, no autocontrast (autocontrast per channel
    would move hues, which is the one thing this must not do).

    IT DECIDES NOTHING, and that is a measured decision rather than caution --
    see the sweep note above plate_problems. It is here because it is the one
    cheap statistic that is LOW exactly where border_flatness's known false
    positive lives: a border split between two materials of the same lightness,
    flat sky over flat grass, reads 0.740 flat and 0.461 colour-flat. A blank
    paper card reads high on both (the six cards of the 2026-08-14 wave: 0.750 ->
    0.745, 0.828 -> 0.825, 0.836 -> 0.834, 0.909 -> 0.904, 0.913 -> 0.904,
    0.968 -> 0.966). So a refusal with a LOW colour number is the shape a
    two-material border makes, and the refusal text says to go and look.
    """
    import statistics

    px = im.convert("RGB").load()
    w, h = im.size
    band = max(2, int(min(w, h) * PLATE_BAND))
    vals = [px[x, y] for y in range(0, h, 2) for x in range(0, w, 2)
            if x < band or x >= w - band or y < band or y >= h - band]
    med = [statistics.median([c[i] for c in vals]) for i in range(3)]
    return sum(1 for c in vals
               if all(abs(c[i] - med[i]) <= PLATE_COLOUR_TOL
                      for i in range(3))) / len(vals)


def measure_plate(blob: bytes) -> float:
    """Flatness of an image's bytes, cropped as the box crops it."""
    import io

    from PIL import Image

    return border_flatness(cover_crop(Image.open(io.BytesIO(blob))))


def measure_plate_colour(blob: bytes) -> float:
    """Colour flatness of an image's bytes, cropped as the box crops it."""
    import io

    from PIL import Image

    return border_colour_flatness(cover_crop(Image.open(io.BytesIO(blob))))


def plate_acks(spec: dict) -> list:
    """Every acknowledgement written on a spec: one string, or a list of them.

    A single job can trip more than one of these guards at once -- a --src under
    plates-local is BOTH unfetchable and unresolvable -- and a waiver that can
    only ever name one of them is a dead end for exactly the jobs that need it
    most. So `plate_ack:` accepts a list as well as a string; one string stays
    the common case and reads the same as it always did.
    """
    ack = spec.get("plate_ack")
    if ack is None:
        return []
    if isinstance(ack, (list, tuple)):
        return [str(a).strip() for a in ack]
    return [str(ack).strip()]


def acked(spec: dict, reason: str) -> str:
    """The acknowledgement waiving `reason`, or "" if none does.

    Every waiver in this file names the ONE thing it waives, and that is load-
    bearing rather than tidy: "I looked and it is fine" must never cover "I
    could not look". A `card:` ack does not clear an unfetchable --src, and a
    `refs:` ack does not clear a producer that could not be identified.
    """
    for a in plate_acks(spec):
        if a.lower().startswith(reason):
            return a
    return ""


def plate_problems(spec: dict, fetch=None) -> list:
    """Refuse a motion job whose starting picture is not a scene, or is unseen.

    TWO REFUSALS, and the second is deliberate: "I could not check" must never
    read as "fine". An unfetchable or unreadable --src is refused, because half
    this guard's demonstrated value is declining to wave through a picture it
    cannot see -- one of the two the original check could not fetch turned out
    to be cropping the WRONG BEAT'S plate.

    Both are waivable per job and never globally, so the waiver has to name what
    it is waiving, in the spec where a person reads it:

        plate_ack: "card: a deliberate macro close-up of the fruit"
        plate_ack: "unfetchable: hand-staged plate, eyeballed by <who> on <date>"
    """
    if not job_animates(spec):
        return []                 # a blank ground is correct for identity work
    src = crop_src(spec)
    if not src:
        # No crop step: this job names no source picture, so there is nothing
        # for this guard to point at. Its init came from somewhere else and is
        # somebody's eyes to check.
        print("  plate    no --src in any step -- no picture to measure")
        return []
    path = results_branch_path(src)
    blob = (fetch or fetch_results_blob)(path) if path else None
    if blob is None:
        ack = acked(spec, "unfetchable")
        if ack:
            print("  plate    UNFETCHABLE, waived by the spec -- %s" % ack)
            return []
        return ["BLOCKED: could not fetch this job's --src, so its picture was NOT "
                "checked -- and 'could not check' is not 'fine'.\n"
                "      --src %s\n"
                "      The check reads %s, i.e. plates published through a farm-out "
                "job. Publish the plate that way and point --src at it, or waive this "
                "one job with plate_ack: \"unfetchable: <why>\". Two of the 2026-08-14 "
                "wave landed here and one of them was cropping the WRONG BEAT'S plate."
                % (src, RESULTS_BRANCH)]
    try:
        flat = measure_plate(blob)
    except Exception as exc:      # unreadable bytes, no Pillow, a truncated png
        ack = acked(spec, "unfetchable")
        if ack:
            print("  plate    UNREADABLE, waived by the spec -- %s" % ack)
            return []
        return ["BLOCKED: this job's --src could not be measured (%s: %s), so its "
                "picture was NOT checked, which is a refusal and not a pass.\n"
                "      --src %s\n"
                "      Fix the reader (Pillow must be importable here) or waive this "
                "one job with plate_ack: \"unfetchable: <why>\"."
                % (type(exc).__name__, exc, src)]
    if flat < PLATE_FLAT_MAX:
        # Say only what was established. This measured the BORDER, so all it
        # can report is "no blank paper behind the figure" -- it has passed a
        # tight portrait card at 0.236 and a fruit on a bare gradient at 0.060.
        # See the note above; the init still wants a pair of eyes.
        print("  plate    flatness %.3f of %.2f -- no blank-paper card detected. "
              "This measures the BORDER only:" % (flat, PLATE_FLAT_MAX))
        print("           it does NOT establish that a place is depicted, and it "
              "has passed both a")
        print("           tight portrait card and a world-absent macro. OPEN THE "
              "INIT before you")
        print("           trust the wave -- %s" % src)
        return []
    ack = acked(spec, "card")
    if ack:
        print("  plate    flatness %.3f of %.2f reads as a CARD, waived by the spec "
              "-- %s" % (flat, PLATE_FLAT_MAX, ack))
        return []
    try:
        colour = measure_plate_colour(blob)
    except Exception:
        colour = None
    hint = ""
    if colour is not None and colour < PLATE_FLAT_MAX:
        hint = ("      LOOK BEFORE YOU BELIEVE THIS ONE. The same band is only %.3f "
                "flat in COLOUR\n"
                "      (fraction within +/-%d RGB levels of its median colour), and "
                "blank paper is\n"
                "      flat in both -- the six cards this threshold was cut from read "
                "0.745 to 0.966\n"
                "      on the colour statistic too. Flat in lightness and NOT flat in "
                "colour is what a\n"
                "      border made of two materials looks like: sky above, grass below, "
                "same lightness,\n"
                "      different hue. That is a real scene, and this guard refuses one "
                "of them today\n"
                "      (see the KNOWN FALSE POSITIVE note in this file). The colour "
                "number decides\n"
                "      nothing -- swapping to it releases costume sheets -- it only "
                "tells you to open the\n"
                "      picture, which is the only thing that settles it.\n"
                % (colour, PLATE_COLOUR_TOL))
    return [("BLOCKED: the picture this job would animate looks like a CHARACTER CARD, "
             "not a scene -- a figure on flat blank paper with no location.\n"
             "      border flatness %.3f, and %.2f or above is blank paper\n"
             % (flat, PLATE_FLAT_MAX))
            + hint
            + ("      --src %s\n"
               "      Point the job at a real scene plate and enqueue it again. Do not "
               "just re-run it: an animated reference sheet is worthless footage that "
               "still scores near the TOP on frame-difference, which is how six of these "
               "got past everything on 2026-08-14. If it really is a deliberate macro or "
               "close-up, say so in the spec: plate_ack: \"card: <why>\"." % src)]


# --------------------------------------------------------------------------
# The refs check: WHICH REFERENCE SET DREW THE PLATE.
#
# The same 2026-08-14 wave, asked a different question. The flatness check above
# measures the PICTURE; this one checks the ARGUMENT that produced it, and on
# this failure the argument is the better witness -- because the two classes are
# interleaved at the image level and CLEAN at the reference-set level.
#
# MEASURED over every fetchable plate on the results branch, each grouped by the
# reference set of the job that PRODUCED it, scored by the cropped flatness
# above at >=0.62:
#
#     refs set                        n     flagged
#     refs-charref-guards-r5-0812    24     18
#     refs-guards-chosen-0814        24     20
#     refs-goblin-frozen-0812        84     63
#     refs-guards-twoinfield-0813    28      0     (max 0.462)
#     refs-goblin-approved-0814      48      0
#     refs-goblin-head-0812          24      0
#     refs-goblin-scene-0813          -      0
#     refs-founder-pick               -      0
#
# ONE-VARIABLE CONFIRMATION on three beats, same beat and same prompt, only the
# reference set changed: b09's scene-0814 plates (charref-r5 refs) all score
# >=0.94 while its scene-r2-0815 plates (twoinfield refs) all score <=0.09. b06
# and b10 behave identically. So the split is a property of the refs, not of the
# beat or the wording.
#
# AND THIS IS WHY IT IS WORTH CHECKING THE ARGUMENT AT ALL: within the bad sets,
# flatness scores 0.282, 0.492 and 0.583 on sibling seeds -- cards the flatness
# guard walks straight past, from a job whose refs it can name for certain. A
# deterministic fact about the job beats a heuristic about the pixels, when the
# fact is available.
#
# HOW THE PRODUCER IS FOUND. A motion job carries no --refs of its own; refs
# live on the plate-GENERATION job. But the --src path names its producer --
# farm-out/<dir>/<file> is written by some job's publish step -- so <dir> maps
# back to that spec and its --refs. It maps back by NAME when the directory
# happens to be named for the spec file, and otherwise by the destination the
# spec itself declares; see resolve_producer, which is where the assumption that
# only the first of those exists cost 274 of 645 published directories.
#
# A NAME PATTERN IS NOT ENOUGH, and this is the load-bearing part of the design:
# refs-guards-chosen-0814 contains no `charref` tell, no `card`, nothing a
# substring rule could key on, and it is the set with the worst hit rate in the
# table (20 of 24). Any pattern that catches it also catches
# refs-guards-twoinfield-0813, which is 0 of 28. So the list is EXPLICIT.
#
# WHICH MAKES THE LIMIT PLAIN, and the refusal text says it out loud: this is a
# DENYLIST. A card set nobody has listed yet passes unnoticed, and so does a
# producer that used no refs at all. That is the honest shape of the claim --
# a refusal here is a named fact, a pass here is only "not one of the three sets
# we have caught". The flatness pass line was just rewritten for implying more
# than it had; this one is not going to repeat it.
#
# WHICH IS ALSO WHY BOTH GUARDS STAY. They fail in opposite directions: refs is
# deterministic but blind to an unlisted set, flatness is a heuristic but sees
# blank paper whoever drew it. Neither is a substitute for the other and neither
# is a substitute for opening the init.
#
# BUT THEY ARE NOT INDEPENDENT WITNESSES, and this file used to imply they were.
# Read the table above again: the denylist IS border_flatness, thresholded at
# 0.62 and grouped by producing job. The three sets are on it BECAUSE their
# plates score high on the very statistic the plate check reports. So when both
# refusals fire on one job, nothing has been confirmed twice -- one measurement
# has been printed twice, once per pixel and once per producing job. Re-derived
# 2026-08-16 over all 2510 pngs on the branch and the table reproduces:
# charref-guards-r5 63 of 72 flagged, guards-chosen 44 of 96, goblin-frozen 250
# of 312, against twoinfield 0 of 144 and goblin-approved 0 of 192.
#
# THE COST OF THAT IS ON THE BRANCH RIGHT NOW. refs-charref-guards-r5-0812 drew
# farm-out/ep2-b10-patrol-scene-r2-0813/10-no-form-ipa-r0-w010-s1.png, which was
# opened on 2026-08-16 and is a field, a hedge, flowers and two guards -- a
# scene. Both guards refuse it, and the refusals agreeing is not evidence,
# because the set was listed for scoring what that plate also scores.
# correlation_note prints that under any job where both fire.
JOBS_DIR = os.path.join(REPO, "pipeline", "jobs")

# The reference sets that produce costume identity cards. EXPLICIT, because no
# name pattern separates these three from the clean sets -- see the table above.
CARD_REFS_DENYLIST = (
    "refs-charref-guards-r5-0812",
    "refs-guards-chosen-0814",
    "refs-goblin-frozen-0812",
)


def producing_job_id(src: str):
    """The farm-out job id that published this --src, or None.

    farm-out/<job-id>/<file>: the directory is written by the producing job's
    publish step under its own id, so it is the one link a motion job has back
    to the arguments its picture was drawn with.
    """
    path = results_branch_path(src)
    if not path:
        return None                      # plates-local and friends: no producer
    parts = path.split("/")
    return parts[1] if len(parts) > 2 and parts[1] else None


def producer_spec_path(job_id: str, jobs_dir: str = None):
    """The repo spec NAMED for a job id, or None if this machine has no copy.

    The strongest link there is and the first one tried, but it only fires when
    the directory happens to be named for the spec file -- which, measured over
    the whole results branch on 2026-08-16, is true of 371 of 645 published
    directories. See resolve_producer for the other 274.
    """
    for ext in (".yaml", ".yml", ".json"):
        p = os.path.join(jobs_dir or JOBS_DIR, job_id + ext)
        if os.path.isfile(p):
            return p
    return None


# THE DIRECTORY NAME IS DATA, NOT A CONVENTION -- which is the whole reason the
# lookup above is not enough. Every job's publish step is an inline python
# literal written by hand in its own spec:
#
#     dst = "C:/banyan-farm/courier-box/farm-out/ep2-b11-idfix"    # in
#     pipeline/jobs/ep2-b11-idfix-0812.yaml
#
# Nothing derives that string from the spec's `id`, so nothing ever enforced
# that they match, and mostly they do not: the date suffix is usually dropped.
# Measured 2026-08-16 over origin/farm-results-rtx5090: of 645 published
# directories only 371 are named for their spec file. The other 274 were refused
# by refs_problems with "no spec in pipeline/jobs for producing job ..." -- a
# refusal that reads like a provenance gap and was a string mismatch. Beat 11's
# only staging-correct plate sat behind exactly that.
#
# AND THE OBVIOUS REPAIR IS THE WRONG ONE. Looking up `<dir>-<date>` matches 250
# of the 274 and would have been three lines. telemetry.py:171 already records
# why it must not be done: on 2026-08-13 task `ep2-b15-seedC-0813` published into
# `ep2-b15-seedB` and `ep2-b04-balloon-pair-0813` into `ep2-b04-balloon-pair`, so
# "deriving the path from the task name would have produced confident 404s".
# Under a name rule farm-out/ep2-b15-seedB resolves to ep2-b15-seedB-0812 and the
# refs of a DIFFERENT job get read as this plate's provenance. This guard exists
# to answer "what was this picture drawn with"; a confident wrong answer is worse
# than the refusal it replaces.
#
# SO THE INDEX IS BUILT FROM WHAT THE SPEC SAYS ABOUT ITSELF. A spec that writes
# into farm-out/<dir> names <dir> in its own argv, and that is a fact rather than
# a pattern. Measured over the same 645: it resolves 252 of the 274, disagrees
# with the filename lookup on ZERO of the 371 the filename lookup already
# answers, leaves 13 directories that two or more specs genuinely publish into
# (ep2-b13/b14/b15-seedB, the -r2/-r3 pairs, the 13-spec ep2-goblin-staged wave)
# and 9 that no spec in the repo claims at all. The last two groups still refuse.
# An ambiguous directory is a real provenance hazard, not a lookup failure: the
# plate in it could have come from either job and neither answer is checkable.
#
# TERMINAL COMPONENT ONLY, and that is load-bearing. `farm-out/<dir>` at the end
# of a path is a destination directory; `farm-out/<dir>/<file>.png` is a --src
# being READ. Without the distinction ep2-b01-lw-0815 -- which reads
# farm-out/ep2-b01-final055-r3/b01-final055-i55-s0.png and publishes to its own
# directory -- claims to be its own source's producer, and that one directory
# turns ambiguous on a consumer rather than a second producer.
OUT_DIR = re.compile(
    r"courier-box[\\/]+farm-out[\\/]+([A-Za-z0-9._-]+)(?![\\/A-Za-z0-9._-])")


def declared_out_dirs(spec: dict) -> list:
    """The farm-out directories this spec's steps publish INTO.

    Read off argv, like every other claim in this file: the id is written by
    whoever filed the job, the argv is what runs.
    """
    found = []
    for step in spec.get("steps") or []:
        for a in step.get("argv") or []:
            for m in OUT_DIR.finditer(str(a)):
                if m.group(1) not in found:
                    found.append(m.group(1))
    return found


def specs_publishing_to(job_id: str, jobs_dir: str = None, load=None) -> list:
    """Every spec in the repo whose publish step writes farm-out/<job_id>.

    Sorted, so a refusal names its candidates in the same order twice running.
    A spec that cannot be read is skipped rather than fatal -- an unreadable
    neighbour must not decide this job's fate, and the caller refuses anyway
    when nothing resolves.
    """
    d = jobs_dir or JOBS_DIR
    hit = []
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return []
    needle = job_id.encode("utf-8", "replace")
    for name in names:
        if os.path.splitext(name)[1] not in (".yaml", ".yml", ".json"):
            continue
        p = os.path.join(d, name)
        try:
            # Cheap prefilter: a spec whose argv names this directory must
            # contain the string. 810 specs, one substring test each, before
            # any yaml parser is asked to do work.
            with open(p, "rb") as fh:
                if needle not in fh.read():
                    continue
            spec = (load or load_spec)(p)
        except Exception:
            continue
        if isinstance(spec, dict) and job_id in declared_out_dirs(spec):
            hit.append(p)
    return hit


def resolve_producer(job_id: str, jobs_dir: str = None, load=None):
    """(spec path, why not) for a published directory. Exactly one of them is set.

    Two ways to be sure and no third: the spec is NAMED for the directory, or
    exactly one spec in the repo says it publishes there. Anything else refuses,
    and says which -- "two specs publish there" is a different fact from "no spec
    does" and the reader needs to be able to tell them apart.
    """
    named = producer_spec_path(job_id, jobs_dir)
    if named:
        return named, None
    cands = specs_publishing_to(job_id, jobs_dir, load)
    if len(cands) == 1:
        return cands[0], None
    if cands:
        return None, ("%d specs publish into farm-out/%s (%s) -- which of them "
                      "drew this plate is not knowable from the path, so it is "
                      "not guessed at"
                      % (len(cands), job_id,
                         ", ".join(os.path.basename(c) for c in cands)))
    return None, "no spec in pipeline/jobs for producing job %r" % job_id


REPO_DRAFTS = os.path.join(REPO, "pipeline", "wave-drafts.yaml")


def spec_harnesses(spec: dict) -> list:
    """Every distinct --harness directory named anywhere in a spec's steps.

    Every step, for spec_refs' reason and one of its own: a goblin spec names
    the harness on BOTH its dry and its sample step, and on 2026-08-16
    ep2-b18-scale-0816 named `C:\\banyan-farm\\wave-scale-0816` on both while
    every other spec in the tree named `wave-goblin-prep`. A spec that changed
    harness half way through would render its preflight against one wording and
    its picture against another, and nothing downstream would say so.
    """
    seen, out = set(), []
    for step in spec.get("steps") or []:
        argv = step.get("argv") or []
        for i, a in enumerate(argv):
            if str(a) == "--harness" and i + 1 < len(argv):
                raw = str(argv[i + 1]).replace("/", "\\").rstrip("\\")
                if raw.lower() not in seen:
                    seen.add(raw.lower())
                    out.append(raw)
    return out


def box_file_sha256(path: str) -> str:
    """sha256 of a file ON THE BOX, or "" when it cannot be read.

    "" is not "matches" -- every caller treats it as a refusal, for the reason
    the plate check gives: a thing that could not be checked was not checked,
    and "could not check" must not exit zero.
    """
    r = ssh('powershell -NoProfile -Command "(Get-FileHash \'%s\' '
            '-Algorithm SHA256).Hash"' % path)
    if r.returncode != 0:
        return ""
    return (r.stdout or "").strip().lower()


def harness_drafts_problems(spec: dict, repo_sha: str = None,
                            box_sha=box_file_sha256) -> list:
    """Refuse a job whose harness holds a wave-drafts.yaml that is not ours.

    THE FAILURE THIS EXISTS FOR, 2026-08-16. `render_wave_sample.py` and
    `goblin_ipa_sample.py` both resolve the prompts as `harness /
    "wave-drafts.yaml"` -- a COPY on the box, never the repo checkout handed to
    them as `--root`. So which wording a job renders is decided entirely by
    which directory its `--harness` names, and there were SIX copies of that
    file on the card, five of them stale:

      dd644905c2eb  C:\\banyan-farm\\wave-goblin-prep\\wave-drafts.yaml   <- ours
      0017402c4aa0  C:\\banyan-farm\\wave-scale-0816\\wave-drafts.yaml
      2c7b1e2a68b6  C:\\banyan-farm\\banyan-city\\pipeline\\wave-drafts.yaml
      67a5083e7fbc  C:\\banyan-farm\\wave-design-probe\\wave-drafts.yaml
      714d77bc3c30  C:\\banyan-farm\\wave-goblin-prep\\repo\\pipeline\\...
      635fac3a476c  C:\\banyan-farm\\courier-box\\farm-out\\...-src\\...

    FOUR of those five still carried `bounces off his head` on beat 19 -- the
    wording the founder killed on 2026-08-15, and which `done_when` in
    review/ep2-picks/done-definitions.yaml now makes DISQUALIFYING ("a take
    where the fruit touches him fails this beat now, however well it moves").
    A spec pointed at any of them would have rendered a take that is defined as
    a failure and published it as canon, and the only thing distinguishing it
    from a good render would have been a path in its argv.

    WHY THE CHECK IS HERE AND NOT ONLY IN THE RENDERER. The renderer already
    computes this exact number -- `drafts_sha = sha256(drafts_path.read_bytes())`,
    goblin_ipa_sample.py:636 -- and writes it into every sidecar as
    `drafts_sha256`. It has been recording the evidence of this failure on every
    render since the file was written and nothing has ever read it back. So the
    fix is not new plumbing, it is a comparison; and the comparison belongs
    where the repo is, because THE BOX HAS NO FRESH CHECKOUT. Its two repo
    copies are dated 08-13 and 08-15. Only the Mac knows what the current
    wording is, so only the Mac can say whether a copy is stale.

    THE SECOND CHECK, AND WHAT THIS DOCSTRING USED TO CLAIM ABOUT IT. Until
    2026-08-17 the paragraph here read: "The renderer keeps a second, later
    check of its own (see --expect-drafts-sha256) because enqueue time and run
    time are not the same moment: `--backlog` work sits for hours." That flag
    existed in exactly one place in the repo -- this docstring. It was in
    neither sampler, neither wrapper, nor any spec. A false load-bearing
    docstring is worse than a stale one: it closes the investigation, because a
    reader believes the check exists and stops looking. The reasoning was right
    and the check was absent, which is the one combination nobody audits.

    The reasoning is still right, so the flag now exists:

      goblin_ipa_sample.py --expect-drafts-sha256 <hex>   (also reachable
      through goblin_ipa_beat.py, which passes it straight down)

    It re-hashes `<harness>/wave-drafts.yaml` at RENDER time, before a module is
    imported or a weight touched, and exits 12 having drawn nothing if the
    wording moved between filing and running. A >=8-digit prefix is accepted;
    an unusable one refuses rather than being skipped. IT IS OPT-IN AND INERT
    WHEN ABSENT -- it was added to shared renderer plumbing with jobs in flight,
    so nothing acquires the check by accident. Nothing here injects it yet:
    THIS function still passes/refuses a spec on the enqueue-time comparison
    alone, and a spec gets the run-time check only by naming the flag in its own
    argv. Two things gate turning that into an automatic injection: every box
    copy of goblin_ipa_sample.py must first hold the flag (an older copy dies on
    an unknown argument), and someone must decide whether a job should be
    KILLED or merely reported when a peer legitimately re-syncs the harness
    under it. Until then, `--expect-drafts-sha256 <hash>` in the spec is the
    whole interface.

    AND FOR EVERY JOB THAT RAN WITHOUT IT, including all of them before today:
    the mismatch is still detectable after the fact, because the sidecars record
    it. `python3 pipeline/check_drafts_provenance.py <job-out-dir>` reads
    `drafts_sha256` back and reports which frames were drawn from other wording
    (rc 1 divergence, rc 2 nothing identifiable -- never a silent pass).
    """
    if repo_sha is None:
        repo_sha = file_sha256(REPO_DRAFTS)
    ack = str(spec.get("drafts_ack") or "").strip()
    problems = []
    for harness in spec_harnesses(spec):
        path = harness + "\\wave-drafts.yaml"
        theirs = box_sha(path)
        if not theirs:
            problems.append(
                "harness %s holds no readable wave-drafts.yaml -- the prompts "
                "this job would render cannot be identified, and an unchecked "
                "wording is not a passing one" % harness)
        elif theirs != repo_sha and not ack:
            problems.append(
                "STALE DRAFTS: %s\n"
                "      box  %s\n"
                "      repo %s  (pipeline/wave-drafts.yaml)\n"
                "    This job would render wording the repo has superseded and "
                "publish it as canon.\n"
                "    FIX, one of:\n"
                "      python3 pipeline/box_enqueue.py --sync-drafts   "
                "(copies the repo file to every harness; refuses while the "
                "queue is busy)\n"
                "      repoint --harness at C:\\banyan-farm\\wave-goblin-prep, "
                "the copy that matches\n"
                "    Or, if the drift is DELIBERATE -- a forked wording being "
                "tested on purpose --\n"
                "    say so in the spec and it is recorded in provenance:\n"
                "      drafts_ack: \"<why this harness must not be synced>\""
                % (path, theirs, repo_sha))
        elif theirs != repo_sha:
            print("  drafts  %-46s WAIVED: %s" % (harness, ack))
    return problems


def file_sha256(path: str) -> str:
    import hashlib
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# Only these honour --expect-drafts-sha256. The list is a WHITELIST and not a
# blacklist on purpose: a script that does not know the flag dies on an unknown
# argument, so injecting into anything not named here would break the job it was
# meant to protect. render_wave_sample.py is deliberately absent -- it resolves
# `harness / "wave-drafts.yaml"` exactly the same way and has the same hole, but
# it does not accept the flag yet.
DRAFTS_FLAG = "--expect-drafts-sha256"
DRAFTS_AWARE = ("goblin_ipa_sample.py", "goblin_ipa_beat.py")


def argv_value(argv: list, flag: str):
    """The value following `flag` in an argv, or None."""
    for i, a in enumerate(argv):
        if str(a) == flag and i + 1 < len(argv):
            return str(argv[i + 1])
    return None


def inject_drafts_expectation(job: dict, spec: dict, repo_sha: str = None,
                              box_sha=box_file_sha256):
    """Stamp the wording this job was CLEARED against into its own argv.

    WHY THIS IS AUTOMATIC AND NOT LEFT TO SPEC AUTHORS (Oleg, 2026-08-17,
    deciding the question this function used to only ask). harness_drafts_problems
    above compares the harness wording to ours at FILING time. That comparison
    goes stale the moment it is made: `--backlog` work is promoted hours later,
    and the drafts on the harness get hand-synced in between because
    `--sync-drafts` refuses while the queue is busy. So the filing-time hash is
    written into the job's own command line, and the renderer re-checks it at
    render time and REFUSES TO DRAW on a mismatch -- rc 12, nothing drawn, rather
    than a warning nobody reads.

    "Refuse, don't report" is his ruling and it is the cheap direction: a refused
    job is re-filed in minutes, while a job that renders superseded wording
    publishes it as canon and poisons the provenance record (§7.2). It is the
    same lesson as the runner reporting `State: Running` with the GPU at 0%.

    WHICH HASH GETS STAMPED, and it is not always the repo's. Normally the two
    are equal -- the job would have been refused otherwise -- so the repo's hash
    is used and no ssh round trip is spent. But a spec carrying `drafts_ack` is a
    DELIBERATE fork being tested on purpose, and stamping the repo's hash there
    would make the guard kill the very job the ack cleared. So an ack'd spec is
    stamped with the harness's OWN measured hash: the promise is "the wording
    this was cleared against", not "the wording in the repo".

    THE OPERATIONAL CONSEQUENCE, said out loud: after any `--sync-drafts`, every
    backlog job filed against the older wording will refuse at render time and
    has to be re-filed. That is the intended behaviour and not a bug -- those
    jobs were cleared against words that no longer exist.

    Returns (job, notes). Never mutates the spec or the caller's step dicts.
    """
    steps_in = job.get("steps") or []
    ack = str(spec.get("drafts_ack") or "").strip()
    notes, steps, changed = [], [], False
    for step in steps_in:
        argv = [str(a) for a in (step.get("argv") or [])]
        names = {a.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1] for a in argv}
        harness = argv_value(argv, "--harness")
        if not names & set(DRAFTS_AWARE) or harness is None:
            steps.append(step)
            continue
        if DRAFTS_FLAG in argv:
            # An author who wrote it themselves outranks us: they may be pinning
            # a wording on purpose, and two copies of the flag is an argparse
            # error rather than a belt and braces.
            notes.append("step %s already pins %s %s -- left alone"
                         % (step.get("name"), DRAFTS_FLAG,
                            argv_value(argv, DRAFTS_FLAG)))
            steps.append(step)
            continue
        want = repo_sha if repo_sha is not None else file_sha256(REPO_DRAFTS)
        if ack:
            want = box_sha(harness + "\\wave-drafts.yaml")
            if len(want or "") != 64:
                # Unreachable in practice -- harness_drafts_problems refuses an
                # unreadable harness before this runs -- and if it ever is
                # reached, a job with no expectation is the state we already
                # had, not a new failure. Said out loud rather than silently.
                notes.append("step %s: harness drafts unreadable, NO run-time "
                             "check stamped (enqueue-time comparison only)"
                             % step.get("name"))
                steps.append(step)
                continue
        steps.append(dict(step, argv=argv + [DRAFTS_FLAG, want]))
        changed = True
        notes.append("step %s: run-time drafts check stamped, %s%s"
                     % (step.get("name"), want[:12],
                        " (harness's own, drafts_ack)" if ack else ""))
    if not changed and not notes:
        return job, notes
    return dict(job, steps=steps), notes


def spec_refs(spec: dict) -> list:
    """Every --refs basename named anywhere in a spec's steps.

    Every step, not the first: a goblin spec names the same refs on its dry and
    its sample step, and a spec that changed refs half way through is exactly
    the one worth catching.
    """
    names = []
    for step in spec.get("steps") or []:
        argv = step.get("argv") or []
        for i, a in enumerate(argv):
            if str(a) == "--refs" and i + 1 < len(argv):
                raw = str(argv[i + 1]).replace("\\", "/").rstrip("/")
                names.append(raw.rsplit("/", 1)[-1])
    return names


def refs_problems(spec: dict, jobs_dir: str = None, load=None) -> list:
    """Refuse a motion job whose plate was drawn with a card reference set.

    TWO REFUSALS again, and the second for the same reason as the plate check's:
    a producer that cannot be identified was not checked, and "could not check"
    must not exit zero.

    WHAT "CANNOT BE IDENTIFIED" MEANS WAS WRONG UNTIL 2026-08-16, and this
    docstring said so in its own words: "ep2-b01-final055-r3, whose spec is
    simply absent from pipeline/jobs". It is not absent. It is
    pipeline/jobs/ep2-b01-final055-r3-0812.yaml, and the directory it published
    into simply does not carry the date. That mistake was not one spec's: it
    refused 274 of the 645 directories on the results branch. resolve_producer
    now reads the destination each spec declares for itself, and the refusal
    below fires only when no spec claims the directory or when more than one
    does -- the second being a real hazard rather than a lookup failure.

    Each is waivable per job, and separately, because they are different claims:

        plate_ack: "refs: this set's b21 seed is a real field, checked by <who>"
        plate_ack: "unresolved: plate hand-staged from <job>, refs read by <who>"
    """
    if not job_animates(spec):
        return []                 # card refs are the POINT of identity work
    src = crop_src(spec)
    if not src:
        # Same stance as the plate check: this job names no source picture, so
        # there is no producer to trace. Its init came from somewhere else.
        print("  refs     no --src in any step -- no producing job to trace")
        return []
    job_id = producing_job_id(src)
    path, why = ((None, "no farm-out job id in that path") if not job_id
                 else resolve_producer(job_id, jobs_dir, load))
    if path is None:
        producer = {}
    else:
        try:
            producer = (load or load_spec)(path) or {}
        except Exception as exc:   # malformed yaml, no pyyaml, unreadable file
            # A crash here would abort the enqueue with a traceback instead of a
            # refusal. Same law, said the same way: unreadable is unchecked.
            why = "producer spec %s could not be read (%s: %s)" % (
                os.path.basename(path), type(exc).__name__, exc)
            producer = {}
    if why:
        ack = acked(spec, "unresolved")
        if ack:
            print("  refs     UNRESOLVED producer, waived by the spec -- %s" % ack)
            return []
        return ["BLOCKED: could not work out which job produced this job's --src, so "
                "the reference set it was drawn with was NOT checked -- and 'could "
                "not check' is not 'fine'.\n"
                "      --src %s\n"
                "      %s\n"
                "      The check reads farm-out/<dir>/<file>, then takes the spec "
                "NAMED <dir> or, failing that, the one spec whose own publish step "
                "writes into <dir>. Two specs writing there is not a tie to break: "
                "the plate could be either job's and the answer would not be "
                "checkable. Publish the plate through a farm-out directory one spec "
                "owns and point --src at it, or waive this one job with plate_ack: "
                "\"unresolved: <why>\"." % (src, why)]
    refs = spec_refs(producer)
    bad = sorted({r for r in refs if r in CARD_REFS_DENYLIST})
    if not bad:
        # Say only what was established. This is a DENYLIST of three sets; it
        # cannot know anything about a fourth.
        print("  refs     producer %s used %s -- none on the card denylist. That is a "
              "DENYLIST"
              % (job_id, ", ".join(sorted(set(refs))) if refs else "no reference set"))
        print("           of %d known card sets, so a NEW unlisted set passes here "
              "unseen, and so" % len(CARD_REFS_DENYLIST))
        print("           does a producer that used no refs at all. It does NOT "
              "establish the plate is a scene.")
        return []
    ack = acked(spec, "refs")
    if ack:
        print("  refs     producer %s used card set %s, waived by the spec -- %s"
              % (job_id, ", ".join(bad), ack))
        return []
    return ["BLOCKED: the plate this job would animate was drawn by job %s from the "
            "COSTUME CARD reference set %s -- the sets that produce a figure on blank "
            "paper with no location and no second character.\n"
            "      --src %s\n"
            "      Measured over every fetchable plate on the results branch: that "
            "set flags on border flatness where refs-guards-twoinfield-0813 (0 of 28) "
            "and refs-goblin-approved-0814 (0 of 48) never do, and b06/b09/b10 flip "
            "clean when only the refs change. Six of the 2026-08-14 wave's nineteen "
            "renders animated a card from these sets.\n"
            "      Re-cut the plate from a scene reference set and point --src at "
            "that job, or waive this one job with plate_ack: \"refs: <why>\".\n"
            "      LIMIT, stated rather than glossed: this is an EXPLICIT DENYLIST of "
            "%d sets and no name pattern would do (refs-guards-chosen-0814 carries no "
            "'charref' tell). A card set nobody has added here yet will slip straight "
            "past this check, as will a producer that named no refs. A pass is not a "
            "clearance -- open the init.\n"
            "      AND THE SET IS NOT ALL CARDS. It was listed for a HIT RATE on "
            "border flatness, not because every plate it drew is a costume sheet: "
            "refs-charref-guards-r5-0812 also drew "
            "ep2-b10-patrol-scene-r2-0813/10-no-form-ipa-r0-w010-s1.png, opened "
            "2026-08-16, which is a field with a hedge, flowers and two guards. If "
            "this is that plate, this refusal is wrong and so is the flatness one -- "
            "for the same reason, because they are the same measurement."
            % (job_id, ", ".join(bad), src, len(CARD_REFS_DENYLIST))]


def output_path_problems(spec: dict) -> list:
    """Would this job write its outputs somewhere nobody will look for them?

    WHAT THIS IS FOR, measured 2026-08-17. Six jobs were filed, all six rendered
    perfectly, and all six failed rc=92 with their frames written into
    C:\\Windows\\System32 -- the runner service's working directory. The card
    then idled for eleven hours because a failed queue is a silent one. The
    cause was a RELATIVE `--out`: the authoring script called
    os.path.basename() on a Windows path from a Mac, where there is no "/" to
    split on, so it returned the whole string and the "replace the basename"
    line replaced the entire absolute path with a bare filename.

    Nothing in this file objected, because every existing check asks what a job
    is ALLOWED to do and none asked whether it can put its output where it says
    it will. These three do:

      1. an output flag whose value is not an absolute Windows path
      2. a declared artifact no step ever names -- the runner fails the job on
         missing artifacts, which is the only reason last night surfaced at all,
         and that check is worth nothing if the list names another job's files
      3. an inline publish step reading a directory this job never writes to.
         The forward-slash spelling is why this one is separate: a relocation
         that rewrote only backslash paths left publish copying the SOURCE job's
         frames into this job's folder, printing "published 14 of 14" and
         exiting 0. It published another job's work under this job's name.

    Returns a list of problems, empty when the spec is sound.
    """
    problems = []
    steps = spec.get("steps") or []
    out_flags = ("--out", "--output", "--out-file", "--mask-out", "--outdir", "--out-dir")
    abs_win = re.compile(r"^[A-Za-z]:[\\/]")

    argv_blobs = []
    for st in steps:
        argv = st.get("argv") or []
        argv_blobs.append(" ".join(str(a) for a in argv))
        for i, a in enumerate(argv):
            if str(a) in out_flags and i + 1 < len(argv):
                val = str(argv[i + 1])
                if not abs_win.match(val):
                    problems.append(
                        "BLOCKED: step %r passes %s %r, which is NOT an absolute path. "
                        "The runner's working directory is C:\\Windows\\System32, so a "
                        "relative output is written there, the artifact check cannot "
                        "find it, and the job fails with the render already done."
                        % (st.get("name"), a, val))
    all_argv = " ".join(argv_blobs)

    for art in spec.get("artifacts") or []:
        base = ntpath.basename(str(art))
        if base and base not in all_argv:
            problems.append(
                "BLOCKED: declared artifact %r is never named by any step. Either the "
                "job does not produce it, or the artifacts list was carried from "
                "another spec -- both make the runner's missing-artifact check "
                "meaningless." % base)

    # 3. an inline publish program must read a directory some step writes into.
    written_dirs = set()
    for st in steps:
        argv = st.get("argv") or []
        for i, a in enumerate(argv):
            if str(a) in out_flags and i + 1 < len(argv):
                d = ntpath.dirname(str(argv[i + 1]))
                if d:
                    written_dirs.add(d.replace("/", "\\").rstrip("\\").lower())
    for st in steps:
        argv = st.get("argv") or []
        if len(argv) >= 3 and str(argv[1]) == "-c":
            for m in re.finditer(r"""src\s*=\s*['"]([^'"]+)['"]""", str(argv[2])):
                d = m.group(1).replace("/", "\\").rstrip("\\").lower()
                if written_dirs and d not in written_dirs:
                    problems.append(
                        "BLOCKED: step %r reads src=%r, which no step in this job writes "
                        "to (this job writes: %s). A publish step pointed at another "
                        "job's directory copies that job's frames out under this job's "
                        "name and exits 0."
                        % (st.get("name"), m.group(1), ", ".join(sorted(written_dirs))))
    return problems


def courier_problems(spec: dict) -> list:
    """Will anything ever CARRY this job's outputs off the box?

    WHAT THIS IS FOR, measured 2026-08-19 and it cost two days.
    `ep2-cnet-probe-0817` ran on 2026-08-17 at 12:39-12:41Z and every one of its
    four arms completed. NOBODY KNEW. Its spec carried no outcome block, two
    commits said it had been deliberately held back, its own driver commit said
    "Not run yet", every `C:\\banyan-queue\\*` directory was empty and a repo-wide
    find for *cnet* returned only the spec and a research note -- so two later
    documents state as fact that it never fired. The renders were sitting in
    `C:\\banyan-farm\\cnet-probe-0817\\out\\` the whole time. When they were
    finally pulled they PASSED, 28x and 17x over a bar pre-registered in code.

    The cause is one missing step. The spec declares `artifacts:` under its own
    working directory and NOTHING EVER COPIES THEM to
    `C:\\banyan-farm\\courier-box\\farm-out\\`, which is the only path by which a
    box result reaches this tree -- the runner pushes from there and from
    nowhere else. Every other job of that era ends with an inline `python -c`
    that copies its named files there and writes a .sha256; this one just
    stopped.

    output_path_problems above asks whether the declared artifacts are NAMED by
    some step. That check passed here, and passing it is worthless on its own:
    NAMED IS NOT DELIVERED. A job can produce exactly what it promised, in
    exactly the place it promised, and still be invisible to everyone who needed
    it. So this asks the next question -- does any step put those bytes where
    the courier looks?

    THE BLAST RADIUS WAS MEASURED BEFORE THIS WENT IN, not assumed. Run over
    every spec in pipeline/jobs (962 of them declare artifacts), it refuses 100:
    88 ep1 specs and 9 ep2 specs all dated 0811-0812, which is the era BEFORE
    courier-box existed and results came back another way -- plus
    ep2-cnet-probe-0817. So from the whole courier era it fires on exactly one
    spec, and that spec is the incident. Those older specs are refused only if
    somebody re-files one, and if they do, the refusal is correct: their
    outputs would strand today for the same reason this one did.

    Returns a list of problems, empty when the spec is sound.
    """
    COURIER = r"c:\banyan-farm\courier-box\farm-out"
    arts = [str(a) for a in (spec.get("artifacts") or [])]
    if not arts:
        return []          # a job that promises no artifact strands nothing
    stranded = [a for a in arts if not norm_dest(a).startswith(COURIER)]
    if not stranded:
        return []          # it writes straight into the courier's own directory

    # Two ways a step can be the courier, and both are real in this repo:
    # an inline program that copies files there, and a driver whose --out IS
    # a path under farm-out. Anything else -- merely mentioning the path in a
    # comment, say -- must not count, or the check waves through the exact
    # spec that caused this.
    copy_verbs = ("shutil.copy", "copyfile", "copytree", "copy2", "xcopy",
                  "robocopy", "copy /y", ".write(", "open(")
    out_flags = ("--out", "--output", "--out-file", "--mask-out", "--outdir",
                 "--out-dir", "--publish-to", "--dest")
    for st in spec.get("steps") or []:
        argv = [str(x) for x in (st.get("argv") or [])]
        for i, x in enumerate(argv):
            if x in out_flags and i + 1 < len(argv):
                if norm_dest(argv[i + 1]).startswith(COURIER):
                    return []
        blob = " ".join(argv)
        low = blob.replace("/", "\\").lower()
        if COURIER in low and any(v in blob for v in copy_verbs):
            return []

    return ["BLOCKED: this job declares artifacts that live OUTSIDE "
            "C:\\banyan-farm\\courier-box\\farm-out and no step copies them into "
            "it, so nothing will carry them off the box -- the courier pushes "
            "from farm-out and from nowhere else. Stranded: %s. This is exactly "
            "how ep2-cnet-probe-0817 was lost: it rendered all four arms "
            "successfully on 2026-08-17 at 12:39-12:41Z, its outputs sat in "
            "C:\\banyan-farm\\cnet-probe-0817\\out for TWO DAYS, and the repo "
            "recorded it as never having run in two separate documents until "
            "someone looked at the box by hand on 2026-08-19 -- at which point "
            "it PASSED its own pre-registered bar. Add a publish step that "
            "copies the named files into "
            "C:\\banyan-farm\\courier-box\\farm-out\\<job-id>\\ and writes a "
            ".sha256 beside them." % ", ".join(ntpath.basename(a) for a in stranded)]


# Tools whose OUTPUT FILENAME is derived from an `--arm` flag rather than
# written out anywhere in the spec. Both write into their `--out` DIRECTORY
# under a basename that carries the arm verbatim:
#
#   controlnet_plate.py:491/528  out_dir / ("%s-%s.png" % (--task, --arm))
#   controlnet_probe.py:243      out_dir / f"{TASK}-{a.arm}.png"
#
# The list is a WHITELIST and stays one. Three other scripts in this tree take
# `--arm` and are deliberately absent, because for them the arm is NOT the
# filename: render_b06r6.py:584 and render_b06r7.py name the frame after
# `arm["set"]`, and goblin_ipa_sample.py:884 after a `tag` -- so the assertion
# below would be false on them, and a guard that is false somewhere gets
# switched off everywhere. render_b01r9.py does embed the literal arm
# (`{BEAT}-{slug}-{SET}-{arm}-s{i}.png`) but adds a `-s{i}` seed suffix, which
# is a second derivation this check does not model; three specs use it, none
# has stranded, and inventing the rule for it is exactly what was not asked.
ARM_NAMED_OUTPUT_TOOLS = ("controlnet_plate.py", "controlnet_probe.py")


def _inline_str_vars(body: str) -> dict:
    """`name = "literal"` assignments in an inline `python -c` program.

    Publish steps are written as `glob.glob(out_dir + "/<task>-<arm>.png*")`,
    so the directory the pattern is rooted in is a variable and the check
    cannot see where the pattern points without resolving it.
    """
    vals = {}
    for pat in (r'^\s*(\w+)\s*=\s*"([^"\n]*)"\s*$', r"^\s*(\w+)\s*=\s*'([^'\n]*)'\s*$"):
        for m in re.finditer(pat, body, re.M):
            vals.setdefault(m.group(1), m.group(2))
    return vals


def _glob_call_args(body: str) -> list:
    """The argument expression of every `glob.glob(...)` in an inline program."""
    args, i = [], 0
    while True:
        j = body.find("glob.glob(", i)
        if j < 0:
            return args
        k = j + len("glob.glob(")
        depth = 1
        while k < len(body) and depth:
            if body[k] == "(":
                depth += 1
            elif body[k] == ")":
                depth -= 1
            k += 1
        args.append(body[j + len("glob.glob("):k - 1])
        i = k


def _concat_value(expr: str, vals: dict):
    """`out_dir + "/x-y.png*"` -> the string it builds, or None if it cannot.

    None means "not resolvable", and a pattern this cannot resolve is left
    alone rather than guessed at.
    """
    parts = []
    for term in expr.split("+"):
        t = term.strip()
        if len(t) >= 2 and t[0] in "\"'" and t[-1] == t[0]:
            parts.append(t[1:-1])
        elif t in vals:
            parts.append(vals[t])
        else:
            return None
    return "".join(parts) if parts else None


def arm_name_problems(spec: dict) -> list:
    """Does the spec look for the file the `--arm` flag actually makes?

    WHAT THIS IS FOR, measured 2026-08-21 and it fired on fourteen specs. The
    eight `ep2-b04-tileread-*-0820` rungs rendered rc=0 -- eight good pictures,
    on the card, in their out\\ directories -- and every one of the eight JOBS
    exited rc=1. Their publish step globbed `<task>-hintskel.png` while
    `--arm nocontrol` makes controlnet_plate.py write `<task>-nocontrol.png`,
    so the publish copied nothing, the `>= 4` gate failed, the artifacts check
    found nothing, and the queue recorded eight failures it did not have. The
    same defect sat in six `ep2-b02-adultplate-*-0820` specs beside them.

    The arm name is TYPED into the glob and into `artifacts:`, and DERIVED by
    the tool from a flag three lines further up the same argv. Nothing compared
    the two. Every check above this one asks whether the job may run or whether
    its output can be found at all; this one asks whether the two spellings of
    the same filename, in the same spec, agree. It is one string compare, it
    needs no box and no render, and it refuses before the GPU pays.

    The refusal names BOTH strings, because the fix is a choice between them --
    the arm may be the typo just as easily as the glob is.

    IT IS PER OUTPUT DIRECTORY, NOT PER STEP, AND THAT IS NOT A DETAIL. A
    four-arm spec runs four steps into ONE out dir -- `ep2-cnet-probe-0817` is
    exactly that -- so "this path does not name step 3's arm" is TRUE of every
    correct path in it. The question a multi-arm spec can actually answer is
    whether a path names SOME arm the job writes into that directory, and
    whether every arm it writes is named by SOMETHING. Both directions are
    checked because both are the same strand:

      1. a path naming an arm no step produces -- the b04 failure exactly, and
         it publishes nothing while the picture sits in out\\
      2. an arm no path names -- the same picture stranded, reached from the
         other side. In a one-arm spec these are one bug seen twice, which is
         why b04 tripped both; in a multi-arm spec only direction 2 sees an
         arm that was rendered and then quietly left behind.

    BLAST RADIUS MEASURED BEFORE THIS WENT IN, over all 1211 specs in
    pipeline/jobs: 145 declare a step with an arm-named output, and with the
    fourteen sites already corrected by hand it refuses none of them.

    Returns a list of problems, empty when the spec is sound.
    """
    steps = spec.get("steps") or []
    by_dir = {}                     # normalised out dir -> [(step name, arm)]
    for st in steps:
        argv = [str(x) for x in (st.get("argv") or [])]
        if not any(ntpath.basename(a).lower() in ARM_NAMED_OUTPUT_TOOLS
                   for a in argv):
            continue
        arm = argv_value(argv, "--arm")
        out = argv_value(argv, "--out")
        if arm and out:
            by_dir.setdefault(norm_dest(out), []).append((st.get("name"), arm))
    if not by_dir:
        return []

    WHY = ("This is the defect that made eight good ep2-b04-tileread renders "
           "exit rc=1 on 2026-08-21 with the pictures already on the card.")

    def named(base: str, arm: str) -> bool:
        return ("-" + arm).lower() in base.lower()

    def arms_of(d):
        return ", ".join("%s (step %r)" % (a, s) for s, a in by_dir[d])

    # Every png path this spec points at an arm directory, with where it came
    # from, so both directions below read the same list.
    paths = []                      # [(kind, out dir, pattern, basename)]
    for art in spec.get("artifacts") or []:
        art = str(art)
        base = ntpath.basename(art)
        if base.lower().endswith((".png", ".png.meta.yaml")):
            paths.append(("declared artifact", norm_dest(ntpath.dirname(art)),
                          art, base))
    for st in steps:
        argv = [str(x) for x in (st.get("argv") or [])]
        if len(argv) < 3 or argv[1] != "-c":
            continue
        body = argv[2]
        vals = _inline_str_vars(body)
        for expr in _glob_call_args(body):
            pat = _concat_value(expr, vals)
            if not pat:
                continue            # unresolvable is left alone, never guessed
            win = pat.replace("/", "\\")
            base = ntpath.basename(win)
            if ".png" not in base.lower():
                continue
            paths.append(("publish glob", norm_dest(ntpath.dirname(win)),
                          pat, base))

    problems = []
    # DIRECTION 1: a path in an arm directory that names none of its arms.
    for kind, d, pat, base in paths:
        if d not in by_dir:
            continue
        # A bare wildcard names no arm, so it cannot name the WRONG one.
        if base.startswith("*"):
            continue
        if any(named(base, arm) for _s, arm in by_dir[d]):
            continue
        problems.append(
            "BLOCKED: %s %r names an arm this job never renders. The steps "
            "writing into %s pass --arm %s, and the tool derives its output "
            "filename from that flag -- so nothing it writes will ever match "
            "that path. Fix ONE of the two strings (the arm may be the typo as "
            "easily as the path is). %s" % (kind, pat, d, arms_of(d), WHY))

    # DIRECTION 2: an arm rendered into a directory nothing names.
    for d, entries in by_dir.items():
        here = [b for _k, dd, _p, b in paths if dd == d]
        for step, arm in entries:
            if any(b.startswith("*") or named(b, arm) for b in here):
                continue
            problems.append(
                "BLOCKED: step %r renders --arm %r into %s and NO publish glob "
                "or artifacts: entry names %r, so that picture is written and "
                "then left on the card. Named here: %s. %s"
                % (step, arm, d, "-" + arm, ", ".join(sorted(here)) or "nothing",
                   WHY))
    return problems


def gate_checks(spec: dict, job: dict) -> list:
    problems = []
    for key in ("gate", "gate_ref"):
        if spec.get(key):
            problems.append("BLOCKED: spec carries %s: %s -- clearing it is a human "
                            "deleting the key, not this script" % (key, spec[key]))
    if spec.get("recipe_slot"):
        problems.append("BLOCKED: unfilled recipe_slot %r -- the value is the recipe "
                        "and inventing one is scaling an unapproved result"
                        % spec["recipe_slot"])
    if not spec.get("consumer"):
        problems.append("no consumer named -- standing rule is no work without one")
    node = job.get("node")
    if node:
        ok, detail = node_is_approved(node)
        print("  node %-28s %s" % (node, detail))
        if not ok:
            problems.append("node %s is NOT founder-approved -- enqueueing it would "
                            "SystemExit the daemon, not just fail the job" % node)
    elif job["needs_gpu"]:
        problems.append("gpu job names no node, so approval cannot be checked")
    # Two readings, and both stay -- but they are NOT independent, and saying so
    # is the whole of this block. The plate check runs first because its
    # unfetchable refusal is the one that has never been wrong; the refs check
    # then asks what the picture was drawn FROM. A job can honestly trip both.
    # What it must never do is read that as corroboration: the denylist the refs
    # check consults was built by scoring plates with the plate check's own
    # border_flatness, so "card" twice is one statistic twice. correlation_note
    # appends that sentence whenever both card refusals fire together.
    plate = plate_problems(spec)
    refs = refs_problems(spec)
    problems += plate + refs + correlation_note(plate, refs)
    # Independent of both, and of the node gate above: those ask what the
    # picture is drawn FROM, this asks what WORDS get sent. A job can pass every
    # other check in this file and still render a superseded line, because the
    # wording lives in a file on the box that nothing compares to ours.
    problems += harness_drafts_problems(spec)
    # Where the outputs LAND. Every check above asks whether the job is allowed
    # to run; this one asks whether anyone will be able to find what it made.
    problems += output_path_problems(spec)
    # And the half that one cannot see: NAMED IS NOT DELIVERED. A job can write
    # exactly what it promised, exactly where it promised, and still never reach
    # this tree because nothing carries it to the courier's directory.
    problems += courier_problems(spec)
    # And the third way an output goes missing, which neither of those two can
    # see: the job publishes a filename the tool never writes, because the arm
    # in the path was typed and the arm in the filename is derived from a flag.
    problems += arm_name_problems(spec)
    return problems


def correlation_note(plate: list, refs: list) -> list:
    """Say it out loud when the two card refusals are one signal, not two.

    Only when BOTH fired on the card question. The unfetchable and unresolved
    refusals are genuinely independent of the border statistic -- one is "the
    bytes are not here", the other "the producing spec is not here" -- and must
    not be tarred with this.
    """
    if not (any("CHARACTER CARD" in p for p in plate)
            and any("COSTUME CARD reference set" in p for p in refs)):
        return []
    return ["NOTE: the two refusals above are ONE SIGNAL, NOT TWO. The reference "
            "sets in CARD_REFS_DENYLIST were selected by scoring plates with the "
            "same border_flatness the first refusal reports, at the same 0.62. "
            "So the refs check agreeing with the flatness check is not "
            "corroboration -- it is the same measurement, rolled up by producing "
            "job. Two agreeing guards would be a reason to skip opening the "
            "picture; these are not. Open it."]


def norm_dest(dest: str) -> str:
    """A box path in the one spelling two specs can be compared in.

    The box is Windows: `C:\\banyan-farm\\X` and `c:/banyan-farm/x` are one file,
    and a spec written by hand may use either. Comparing the raw strings would
    let a collision through on nothing but a capital letter.
    """
    s = str(dest).strip().replace("/", "\\").rstrip("\\")
    while "\\\\" in s:
        s = s.replace("\\\\", "\\")
    return s.lower()


def payload_dests(spec: dict) -> list:
    """The box paths a spec writes before its job runs."""
    return [str(d) for d in (spec.get("payload") or {})]


def payload_collisions(mine: dict, entries: list, live_ids, now: float,
                       grace: float = RESERVE_GRACE_SEC) -> list:
    """Problems naming every payload path already claimed by a live job.

    `mine` is a reservation dict (rid/job/ts/dests); `entries` are the ones
    already in the index, which on the second (post-reservation) call includes
    `mine` itself -- matched by `rid`, so a job never collides with its own
    claim. `live_ids` is the set of job ids sitting in the box's ready/ and
    running/ right now, or None for "could not look", which drops the check back
    to the grace window alone.

    A recorded claim blocks when its job is still queued on the box, or when it
    is younger than `grace` -- the second half is what catches a twin enqueued
    during the seconds before its sibling reaches ready/, which is the whole
    original bug and the one case the box could not have answered.

    Two claims written in that same gap would otherwise refuse each other and
    both stall, so ties go to the earlier (ts, job): the first writer proceeds,
    the second is told whose path it is. Refusal is by PATH, not by id -- a job
    re-enqueued while its previous run is still queued is refused too, because
    the harm is identical (its payload overwrites what the queued job will read)
    and it stops being a collision the moment that run leaves the queue.
    """
    mine_paths = {norm_dest(d): d for d in mine.get("dests") or []}
    problems = []
    for e in entries:
        if e.get("rid") == mine.get("rid"):
            continue
        queued = live_ids is not None and e.get("job") in live_ids
        reserved = (now - float(e.get("ts") or 0)) < grace
        if not (queued or reserved):
            continue
        for dest in e.get("dests") or []:
            key = norm_dest(dest)
            if key not in mine_paths:
                continue
            if not queued and (mine.get("ts"), mine.get("job")) < (e.get("ts"), e.get("job")):
                continue  # we claimed it first; the other writer is the one that yields
            problems.append(
                "BLOCKED: payload path %s is already claimed by %s job %s -- payloads "
                "are written at enqueue time, so this one would overwrite that job's "
                "inputs before it runs and the box would render one clip under both "
                "names. Give this job its own directory or its own filenames."
                % (mine_paths[key], "queued" if queued else "just-enqueued", e.get("job")))
    return problems


def read_payload_index(path: str = None) -> list:
    """Every reservation this machine has recorded. Missing file = none yet.

    A damaged line is skipped rather than fatal: the index is a guard's memory,
    and one unparseable row must not become the thing that stops every render.
    """
    path = path or PAYLOAD_INDEX  # read at call time so a test can redirect it
    entries = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("dests"):
                    entries.append(row)
    except OSError:
        pass
    return entries


def reserve_payload(mine: dict, path: str = None) -> None:
    """Claim this job's payload paths BEFORE a byte of payload is sent.

    Recording after the scp would leave the claim unwritten during the seconds
    the scp takes -- which is the window the twin arrived in. One line, one
    append, so a peer lane appending at the same moment cannot interleave with
    it or clobber it the way a rewritten json would.
    """
    path = path or PAYLOAD_INDEX
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(mine, ensure_ascii=False) + "\n")


QUEUE_MARKER = "QUEUE-LISTED"


def parse_queue_listing(stdout: str):
    """Job ids out of a `dir /b` of ready/ and running/, or None for "no answer".

    `dir /b` exits 1 on an EMPTY directory, so a return code cannot tell an empty
    queue from a dead ssh -- and reading a dead ssh as an empty queue is what
    would wave the next collision through. The marker echoed after both listings
    is the difference: it only appears if cmd ran our line to the end.
    """
    out = stdout or ""
    if QUEUE_MARKER not in out:
        return None
    ids = set()
    for line in out.splitlines():
        line = line.strip()
        if line.lower().endswith(".json"):
            ids.add(line[:-5])
    return ids


def queued_job_ids():
    """(ids, None) for what is in ready/, running/ and backlog/, or (None, why).

    BACKLOG COUNTS AS LIVE, and leaving it out would have been a hole exactly
    the width of the original bug. A backlogged job's payload files are written
    at FILING time and sit on the box for hours before box_autofill.py fires it;
    its reservation in the local index goes cold after RESERVE_GRACE_SEC, so
    without this listing a later job naming the same payload paths would be
    waved through and would overwrite the backlogged job's prompt before it ever
    ran -- the 2026-08-13 twin overwrite, with a longer fuse.
    """
    r = ssh('dir /b %s\\ready\\*.json 2>nul & dir /b %s\\running\\*.json 2>nul & '
            'dir /b %s\\backlog\\*.json 2>nul & '
            'echo %s' % (QUEUE_ROOT, QUEUE_ROOT, QUEUE_ROOT, QUEUE_MARKER))
    ids = parse_queue_listing(r.stdout)
    if ids is None:
        return None, (r.stderr or r.stdout or "ssh returned nothing").strip()[:200]
    return ids, None


# --------------------------------------------------------------------------
# 8. THE JOB THAT ALREADY RAN. Twice now, and the second time nobody had even
# looked at what the first run made.
#
#   2026-08-19  ep2-b19-dropmotion-0819 was filed twice, sixteen minutes apart:
#               -1787128259 at 08:30 and -1787129173 at 08:46, seven minutes
#               after the first landed in done/. 264s of GPU on a question the
#               first run had already answered. It did not come through
#               backlog/ (autofill.log reads BACKLOG EMPTY at every tick across
#               the window, and box_autofill.plan_fill DOES dedupe against
#               done/) -- it went straight into ready/, which is what this
#               script does when --backlog is omitted.
#   2026-08-20  ep2-b15-listenroot-0820, ep2-b03-covermid-0820 and
#               ep2-b13-shademid-0820 all finished at 04:56 and sat unread until
#               12:20. The resuming lane re-filed all three clean; b03 re-rendered
#               to completion and produced a byte-identical mp4. The two that had
#               not started were renamed .DUP-already-ran-0820 in ready/ by hand.
#
# WHAT THE QUEUE COULD SEE, AND WHAT IT COULD NOT. Every existing collision
# guard in this file compares against LIVE work, and it compares PAYLOAD PATHS,
# not jobs: payload_collisions refuses a path already claimed by a job in
# ready/, running/ or backlog/. Two consequences the incident write-ups both
# state slightly wrong. A finished job owns nothing -- "it stops being a
# collision the moment that run leaves the queue" is deliberate and correct for
# the overwrite hazard it was built for, and blind to this one. And a spec with
# no `payload:` block was never compared to anything at all, live or not, so
# "box_enqueue refuses a reused id against ready/, running/ and backlog/" was
# never true either; that door is closed here too.
#
# THE KEY IS THE JOB'S CONTENT, NOT ITS NAME, because the name cannot be the
# key: to_job stamps an epoch second onto every id, so two filings of one spec
# are ALREADY different ids and land as two different files in done/. So the
# id is used to FIND candidates (base_job_id strips the stamp back to the spec
# id) and a sha over what actually runs is used to DECIDE.
#
# SAME ID + SAME SHA REFUSES. SAME ID + DIFFERENT SHA PASSES, LOUDLY. That is
# the design call, and it is the opposite of treating the id as a primary key.
# The argument:
#
#   * Every documented failure is an IDENTICAL re-file. Both b19 and the three
#     0820 jobs were the same spec filed twice by a resumed lane; b19's two runs
#     are byte-identical mp4s and so are b03's, eight hours apart. The sha is
#     the only thing that separates that from ordinary work.
#   * Refusing revisions would fire on the normal loop. Diagnose -> fix in the
#     pipeline -> re-render is the standing process, and it edits a spec in
#     place far more often than it renames one. A guard that refuses most of
#     what a lane legitimately does gets switched off -- this file already
#     records the runner watchdog being off for four days after exactly that.
#   * done/ stays readable anyway. Each record is <spec-id>-<epoch>.json and
#     carries its own full steps, so two revisions under one spec id are two
#     distinguishable records, not an ambiguity. That is unlike farm-out/, where
#     resolve_producer refuses an ambiguous directory because the two jobs share
#     one namespace and neither answer is checkable.
#   * The asymmetry of being wrong. A false DUP costs one --again and a line of
#     explanation. A missed DUP costs 264s of card time and a reader who finds
#     two completed records for one question.
#
# A LIVE JOB IS THE ONE EXCEPTION and is refused whatever its sha, because the
# hazard is different: a finished job's outputs exist and can be looked at,
# while a twin filed into ready/ races the original onto the same farm-out
# paths with no human in between. Cancel the queued one or --again; do not run
# both.
#
# WHAT THE SHA COVERS, said exactly, because a hash that is vague about its
# input is worse than none. run_sha256 hashes the steps' argv, env, artifacts,
# needs_gpu and max_attempts -- WHAT RUNS -- plus the `payload:` bodies, and
# deliberately NOT: the stamped id, the task name, step names, backlog filing
# metadata, the --expect-drafts-sha256 this script injects, or anything the
# runner writes into the record afterwards (attempts, rc, started_at,
# finished_at, artifacts_present). Three of those exclusions are load-bearing:
#   - the injected drafts hash, because it is stamped from repo state rather
#     than written by the spec author, so leaving it in would let an unrelated
#     edit to wave-drafts.yaml disguise a genuine duplicate as a revision;
#   - the runner's own keys, because the prior run's record is the only copy of
#     it we have and it must hash to the same number as the file we filed;
#   - the id and task, so a duplicate re-filed under a nudged name is still
#     caught by the sha sweep below.
#
# THE ONE HONEST WEAKNESS. `payload:` is not copied into the job json (to_job
# drops it on purpose), so a job filed BEFORE this change carries no
# spec_sha256 and the only sha recomputable from its record is the argv-only
# one. A revision that changed nothing but a prompt file therefore reads as a
# duplicate against those older records. The refusal says so in as many words
# and names --again. Jobs filed from here on carry the full sha and the
# comparison is exact.
DUP_MARKER = "DUP-SCANNED"
DUP_DIRS = ("done", "failed")

# The job keys that describe what the card will DO. An allow-list rather than a
# deny-list because the runner appends to the record it retires -- started_at,
# attempts, runner_pid, runner_host, rc, failed_step, artifacts_present,
# artifact_notes, unprovenanced -- and a deny-list would have to be extended
# every time it learns a new one, silently reading every finished job as a
# revision until someone noticed.
RUN_KEYS = ("steps", "env", "artifacts", "needs_gpu", "max_attempts")

SAFE_ID = re.compile(r"\A[A-Za-z0-9._-]+\Z")
# What to_job and --again append: an epoch second, or an --again token, or both.
ID_STAMP = re.compile(r"-(?:again[0-9a-f]+|[0-9]{9,})\Z")


def base_job_id(name: str) -> str:
    """The spec id under a queue filename: <spec-id>[-<epoch>][-again<hex>].json.

    Repeated because both suffixes can be present and --again stacks on top of
    the epoch. Nine digits minimum for the epoch so a date-suffixed spec id --
    ep2-b15-listenroot-0820, and nearly every spec in pipeline/jobs is one --
    keeps its own tail.
    """
    s = str(name).strip()
    if s.lower().endswith(".json"):
        s = s[:-5]
    while True:
        shorter = ID_STAMP.sub("", s)
        if shorter == s:
            return s
        s = shorter


def canonical_run(job: dict) -> dict:
    """The part of a job that decides what the card renders. See note above.

    Step NAMES are dropped with the other cosmetics: a renamed step runs the
    identical command, and calling that a revision would wave through the exact
    re-file this guard exists to catch. `allow_fail` stays -- it changes whether
    a failing step stops the job.
    """
    steps = []
    for step in job.get("steps") or []:
        argv, skip = [], False
        for a in [str(x) for x in (step.get("argv") or [])]:
            if skip:                       # the value after --expect-drafts-sha256
                skip = False
                continue
            if a == DRAFTS_FLAG:
                skip = True
                continue
            argv.append(a)
        steps.append({"argv": argv, "allow_fail": bool(step.get("allow_fail"))})
    out = {k: job.get(k) for k in RUN_KEYS if k in job}
    out["steps"] = steps
    return out


def run_sha256(job: dict, payload: dict = None) -> str:
    """sha256 over what this job runs, and over the files it is handed.

    Two shas, not one, and the caller picks: WITH payload for the number stamped
    into the job and compared exactly against another stamped job, WITHOUT it for
    the only comparison a pre-2026-08-20 record can support.
    """
    import hashlib

    blob = json.dumps(canonical_run(job), sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))
    if payload:
        bodies = {norm_dest(d): (b if isinstance(b, str)
                                 else json.dumps(b, sort_keys=True))
                  for d, b in payload.items()}
        blob += "\n" + json.dumps(bodies, sort_keys=True, ensure_ascii=False,
                                  separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def with_run_sha(job: dict, payload: dict = None) -> dict:
    """Stamp the job with its own content hash, for the NEXT filing to compare.

    Rides to the box as an unknown key the runner ignores and the sidecar keeps,
    which makes it provenance (§7.2) as well as a guard input: a record on the
    results branch now says which spec content produced it, exactly.
    """
    return dict(job, spec_sha256=run_sha256(job, payload))


def dup_scan_command(base: str, sha: str) -> str:
    """One cmd line: the id's records in done/ and failed/, and a sha sweep.

    The wildcard keeps the listing to the handful of files that could match
    instead of the whole of done/; a base id with a character `dir` would read
    as a pattern falls back to listing everything and filtering here, because a
    wrong wildcard would silently list nothing and read as "never ran".

    findstr is the cheap half of the id-independent check: it matches the sha
    inside the records themselves, so a duplicate re-filed under a nudged name
    is caught too. It finds nothing for jobs filed before spec_sha256 existed,
    which is a gap that closes itself as records turn over.
    """
    pat = (base + "*") if SAFE_ID.match(base or "") else "*"
    parts = []
    for d in DUP_DIRS:
        parts.append("echo [%s]" % d)
        parts.append("dir /b %s\\%s\\%s.json 2>nul" % (QUEUE_ROOT, d, pat))
    parts.append("echo [sha]")
    parts.append('findstr /m /c:"%s" %s 2>nul'
                 % (sha, " ".join("%s\\%s\\*.json" % (QUEUE_ROOT, d)
                                  for d in DUP_DIRS)))
    parts.append("echo " + DUP_MARKER)
    return " & ".join(parts)


def parse_dup_listing(stdout: str):
    """{"done": [...], "failed": [...], "sha": [...]}, or None for "no answer".

    parse_queue_listing's reason, one directory further on: `dir /b` and findstr
    both exit 1 on finding nothing, so only the marker echoed at the end of the
    line separates an empty done/ from a dead ssh -- and reading a dead ssh as
    "never ran" is the whole failure.
    """
    out = stdout or ""
    if DUP_MARKER not in out:
        return None
    found = {"done": [], "failed": [], "sha": []}
    section = None
    for line in out.splitlines():
        line = line.strip()
        if not line or line == DUP_MARKER:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if section == "sha":
            # findstr prints "FINDSTR: Cannot open ...*.json" when a directory
            # is empty, and that line ends in .json too. Only full paths under
            # the queue root count.
            if (line.lower().startswith(QUEUE_ROOT.lower())
                    and line.lower().endswith(".json")):
                found["sha"].append(line)
        elif section in found and line.lower().endswith(".json"):
            found[section].append(line)
    return found


def prior_runs(base: str, sha: str):
    """(listing, None) for what done/ and failed/ hold, or (None, why)."""
    r = ssh(dup_scan_command(base, sha))
    found = parse_dup_listing(r.stdout)
    if found is None:
        return None, (r.stderr or r.stdout or "ssh returned nothing").strip()[:200]
    return found, None


def box_job_record(path: str):
    """A finished job's own json, read off the box, or None.

    None is "could not read", never "not a duplicate" -- duplicate_problems
    refuses on it, for the reason every other unfetchable in this file refuses.
    """
    r = ssh('type "%s"' % path)
    text = r.stdout or ""
    if r.returncode != 0 or "{" not in text:
        return None
    try:
        record = json.loads(text[text.index("{"):])
    except ValueError:
        return None
    return record if isinstance(record, dict) else None


def _ran_when(record: dict, name: str) -> str:
    """When the prior run finished, in whatever the record can support."""
    for key in ("finished_at", "started_at"):
        if record.get(key):
            return str(record[key])
    # Nothing recorded: the epoch this script stamped into the filename is the
    # only clock left, and it says when the job was FILED rather than when it
    # finished. Labelled as such rather than passed off as the finish time.
    stem = name[:-5] if name.lower().endswith(".json") else name
    stamp = re.search(r"-([0-9]{9,})(?:-again[0-9a-f]+)?\Z", stem)
    if stamp:
        return "filed %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime(int(stamp.group(1))))
    return "time not recorded"


def duplicate_problems(job: dict, sha: str, found: dict, live_ids=None,
                       spec_path: str = None, read=None) -> list:
    """Refuse a job the card has already run, or is about to run.

    `found` is a parse_dup_listing dict, `live_ids` the set from queued_job_ids
    (or None for "not looked", which drops the live half only), `read` fetches a
    finished record by box path so a test can hand one over without ssh.
    """
    read = read or box_job_record
    base = base_job_id(job.get("id") or "")
    invocation = ("python3 pipeline/box_enqueue.py %s --again"
                  % (spec_path or ("pipeline/jobs/%s.yaml" % base)))
    problems = []

    for jid in sorted(live_ids or ()):
        if base_job_id(jid) != base:
            continue
        problems.append(
            "BLOCKED: %s is ALREADY QUEUED on the box as %s.json -- it has not run "
            "yet, so filing a second copy does not add an answer, it adds a race: "
            "both would publish into the same farm-out directory with nobody "
            "between them.\n"
            "      See what is waiting:  python3 pipeline/box_enqueue.py --list\n"
            "      Then either let that one run, or park it (.DUP-already-ran) and "
            "file this deliberately:\n"
            "        %s" % (base, jid, invocation))

    for other in sorted(found.get("sha") or ()):
        if base_job_id(other.rsplit("\\", 1)[-1]) == base:
            continue                    # its own id's records are handled below
        problems.append(
            "BLOCKED: a job with BYTE-IDENTICAL content to this one has already run "
            "on the box, under a different name.\n"
            "      %s\n"
            "      spec_sha256 %s -- same steps, same argv, same payload, so it "
            "would render the same frames to the same paths. Look at what that job "
            "made before spending the card again.\n"
            "      Deliberate re-run:  %s" % (other, sha, invocation))

    for where in DUP_DIRS:
        for name in sorted(found.get(where) or ()):
            if base_job_id(name) != base:
                continue                # the wildcard is a prefix, not the answer
            path = "%s\\%s\\%s" % (QUEUE_ROOT, where, name)
            record = read(path)
            if record is None:
                problems.append(
                    "BLOCKED: %s has a record in %s/ (%s) and it could not be read, "
                    "so whether this is the SAME job or a revision of it was NOT "
                    "established -- and 'could not check' is not 'fine'.\n"
                    "      Read it by hand:  ssh %s type %s\n"
                    "      Or file anyway, deliberately:  %s"
                    % (base, where, name, SSH_HOST, path, invocation))
                continue
            theirs, exact = record.get("spec_sha256"), True
            mine = sha
            if not theirs:
                # Filed before spec_sha256 existed. The argv-only sha is the most
                # its record can support, and it cannot see `payload:`.
                theirs, mine, exact = (run_sha256(record), run_sha256(job), False)
            if theirs != mine:
                print("  dup      %s ran before as %s (%s/, %s) and the spec has "
                      "CHANGED since --" % (base, name, where, _ran_when(record, name)))
                print("           filing it as a revision. %s"
                      % ("sha %s -> %s" % (theirs[:12], mine[:12]) if exact else
                         "that record predates spec_sha256, so the comparison "
                         "covered argv only"))
                continue
            problems.append(
                "BLOCKED: this job ALREADY RAN. %s is in %s/ on the box as %s "
                "(finished %s%s).\n"
                "      Nothing that decides what the card renders has changed since"
                "%s, so this would spend the GPU on a question that is already "
                "answered -- 264s of it on 2026-08-19, and again on 2026-08-20 when "
                "three finished jobs were re-filed before anyone read them.\n"
                "      LOOK AT WHAT IT MADE FIRST. The record and its artifacts are "
                "on the box and on the results branch; the first thing a resuming "
                "lane owes a dead one is a look at done/, not a re-file.\n"
                "      Genuinely want it run again -- new seed, a re-measure, "
                "something on the box changed underneath it?\n"
                "        %s"
                % (base, where, name, _ran_when(record, name),
                   "" if record.get("rc") is None else ", rc %s" % record["rc"],
                   "" if exact else
                   " (that record predates spec_sha256, so this compared the steps' "
                   "argv and NOT the `payload:` bodies -- if the only thing you "
                   "changed is a prompt file, that is a revision and --again is the "
                   "right answer)",
                   invocation))
    return problems


def dup_override(problems: list, again: bool, jid: str) -> tuple:
    """(problems, notes) once --again has had its say.

    An override that prints "overridden" and nothing else is a switch, not a
    decision: the refusals are echoed under it so the line that files the job
    also records what it was told and chose to ignore.
    """
    if not again:
        return problems, []
    if not problems:
        # Said out loud rather than passed over. A lane that reached for --again
        # expected a refusal; not getting one usually means it is looking at a
        # different spec than it thinks, and silence would hide that.
        return problems, ["--again given, but nothing refused this job -- it would "
                          "have filed anyway. The id still carries an --again token."]
    notes = ["--again: OVERRIDING %d refusal(s) and filing as %s -- a fresh token, "
             "so this cannot land on the earlier record" % (len(problems), jid)]
    notes += ["  was refused because: " + p.split("\n", 1)[0] for p in problems]
    return [], notes


def send_payload(payload: dict) -> None:
    """Write a spec's `payload:` files onto the box before the job goes live.

    An LTX render needs a positive file, a negative file and a two-stage jobs
    json, all at absolute paths, before its first step runs. Without this every
    render would need a bespoke driver script committed alongside it -- which is
    how the repo has done it so far, one run-bNN.cmd per round, none reusable.
    Shipping them as part of the spec keeps the whole job in one reviewable file.

    Files land BEFORE the job is moved into ready/, so the runner can never
    claim a job whose inputs are still in flight.
    """
    if not payload:
        return
    # Its own directory, not /tmp/payload-<basename>: the box-side collision this
    # script now refuses had a local twin sitting right here. Two lanes sending a
    # payload named b01-fig-prompt.txt shared one staging file, so one lane's text
    # could be scp'd under the other's name -- the same swap, one machine earlier.
    stage = tempfile.mkdtemp(prefix="box-payload-")
    for dest, body in payload.items():
        local = os.path.join(stage, os.path.basename(dest))
        with open(local, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body if isinstance(body, str) else json.dumps(body, indent=2))
        parent = dest.rsplit("\\", 1)[0]
        ssh('if not exist "%s" mkdir "%s"' % (parent, parent))
        cp = subprocess.run(["scp", "-o", "ConnectTimeout=25", local,
                             "%s:%s" % (SSH_HOST, dest.replace("\\", "/"))],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=120)
        if cp.returncode:
            sys.exit("!! payload scp failed for %s: %s" % (dest, cp.stderr or cp.stdout))
        print("  payload -> %s" % dest)


def backlog_problems(spec: dict) -> list:
    """What may NOT be filed for an unattended autofill to fire later.

    ONE REFUSAL, and it is the point of having a separate door. Everything the
    gate_checks above refuse is refused here identically -- filing to the
    backlog runs the whole guard path, because a job that reaches ready/ at 4am
    with nobody watching has had exactly as much checking as this moment gave
    it. What is refused ADDITIONALLY is a spec that only passes because someone
    waived a guard:

        plate_ack: "card: a deliberate macro close-up of the fruit"

    A waiver is a person saying "I looked and it is fine". That is a fine thing
    for a person to say about a job they are enqueueing while awake and about to
    watch. It is not a thing that should still be true hours later when a timer
    fires the job at a plate the lane has since replaced -- and on 2026-08-14 a
    job that took that shortcut turned out to be cropping the WRONG BEAT'S
    plate. So waived work goes in by hand, and box_autofill.py can honestly say
    it has never waived anything.
    """
    if not plate_acks(spec):
        return []
    return ["BLOCKED for --backlog: this spec carries plate_ack: %r. A waiver is a "
            "person vouching for a picture right now; the autofill fires hours later "
            "with nobody looking, so waived work is enqueued by hand instead. Drop "
            "the waiver by fixing what it waives (publish the plate through a "
            "farm-out job and point --src at it), or enqueue this one without "
            "--backlog while you are awake." % plate_acks(spec)]


def with_backlog_meta(job: dict, spec_path: str, expires_h: float) -> dict:
    """Stamp a job with when it was filed and how long it stays true.

    box_autofill.py reads these and refuses to fire an entry older than
    `expires_h` -- a backlog entry names an init and a bar that were true when
    it was written, and the failure mode of a standing queue is firing
    yesterday's recipe at today's plate. The runner ignores keys it does not
    know, so this rides along as provenance into the job's own sidecar.
    """
    job = dict(job)
    job["backlog"] = {"filed_at": int(time.time()),
                      "filed_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      "expires_h": expires_h,
                      "spec": spec_path,
                      "filed_by": "box_enqueue --backlog"}
    return job


# ── GUARD 9: THE CARD'S DISK, WHICH FILLED UP AND FAILED TWO JOBS QUIETLY. ───
# 2026-08-22, 21:12Z. ep2-b15-canonmotion and ep2-b16-canonmotion both died in
# `encode` with `RuntimeError: ios_base::badbit set` out of torch.save, one
# minute apart, on a recipe whose sibling b14 had just passed. Nothing in the
# log says "disk": torch reports a short write as a zip-container length
# mismatch ("unexpected pos 385361152 vs 385361040") and the runner records
# rc=1. C: had 78 MB free of 926 GB.
#
# WHERE IT WENT. Every LTX job writes its prompt embeds and latents as .pt into
# its own C:\banyan-farm\<jobdir>, and nothing has ever deleted them: 368 files,
# 263 GB, across 1256 job directories going back to the first ep2 wave. They are
# pure scratch — re-derived by the encode step from prompt.txt in under a minute
# — while the frames and clips that matter were couriered into farm-out and
# pushed long ago.
#
# WHY THIS IS A PRECONDITION AND NOT A CRON. A full disk does not stop the
# queue; it makes the queue produce failures that read like recipe faults, which
# is the expensive kind of wrong. The lane that hit it was about to re-cut a
# reference and re-word a prompt to explain b15/b16. So the check runs where a
# lane can still be told, at the moment work is filed, and it heals itself
# first: purge scratch older than PURGE_AGE_H (old enough that a claimed job
# cannot own it), re-measure, and only then refuse.
DISK_FLOOR_GB = 40.0        # below this, purge scratch before queueing
DISK_HARD_GB = 8.0          # below this after a purge, refuse — nothing will run
PURGE_AGE_H = 6
PURGE_KEEP = ("banyan-city", "venv", "venv-lora", "courier-box",
              "cnet-openpose-twins", "goblin-ipa-0812")


def box_free_gb():
    """Free GB on the card's C:, or None if the box cannot be reached."""
    r = ssh("fsutil volume diskfree C:", timeout=60)
    if r.returncode:
        return None
    for line in (r.stdout or "").splitlines():
        if "total free bytes" in line.lower() and ":" in line:
            # fsutil prints "Total free bytes : 282,552,942,592 (263.1 GB)".
            # Take the value BEFORE the parenthetical: sweeping every digit in
            # the line silently appends the "2631" of the pretty form and
            # reports a terabyte-scale lie that passes every floor.
            val = line.split(":", 1)[1].split("(")[0]
            digits = "".join(c for c in val if c.isdigit())
            if digits:
                return int(digits) / (1024.0 ** 3)
    return None


def purge_box_scratch(age_h: int = PURGE_AGE_H):
    """Delete .pt scratch from finished job dirs. Returns GB freed, or None."""
    keep = ",".join("'%s'" % n for n in PURGE_KEEP)
    ps = ("$keep=%s; $cut=(Get-Date).AddHours(-%d); "
          "$d=Get-ChildItem C:\\banyan-farm -Directory -Force | "
          "Where-Object { $keep -notcontains $_.Name }; "
          "if (-not $d) { '0'; exit }; "
          "$f=Get-ChildItem $d.FullName -Recurse -File -Force -Filter *.pt "
          "-ErrorAction SilentlyContinue | "
          "Where-Object { $_.LastWriteTime -lt $cut }; "
          "if (-not $f) { '0'; exit }; "
          "$gb=[math]::Round(($f | Measure-Object Length -Sum).Sum/1GB,2); "
          "$f | Remove-Item -Force -ErrorAction SilentlyContinue; $gb"
          % (keep, age_h))
    r = ssh('powershell -NoProfile -Command "%s"' % ps.replace('"', '\\"'),
            timeout=600)
    if r.returncode:
        return None
    for line in reversed((r.stdout or "").strip().splitlines()):
        try:
            return float(line.strip())
        except ValueError:
            continue
    return None


def assert_box_has_room():
    free = box_free_gb()
    if free is None:
        print("  disk: could not read the card's free space -- continuing, but "
              "a job that dies in torch.save is this, not your recipe")
        return
    if free >= DISK_FLOOR_GB:
        print("  disk: %.1f GB free on the card" % free)
        return
    print("  disk: only %.1f GB free on the card (floor %.0f) -- purging .pt "
          "scratch older than %dh" % (free, DISK_FLOOR_GB, PURGE_AGE_H))
    freed = purge_box_scratch()
    after = box_free_gb()
    print("  disk: purge freed %s GB, now %s GB free"
          % ("?" if freed is None else "%.1f" % freed,
             "?" if after is None else "%.1f" % after))
    if after is not None and after < DISK_HARD_GB:
        sys.exit("!! REFUSING TO QUEUE: the card has %.1f GB free and a purge "
                 "of job scratch did not fix it. An LTX encode needs room for "
                 "a ~700 MB .pt and fails as a torch zip-length error, not as "
                 "a disk error -- so this would be filed as a recipe fault. "
                 "Find the real consumer of C: before queueing." % after)


def enqueue(job: dict, dest: str = "ready") -> None:
    assert_box_has_room()
    name = job["id"] + ".json"
    local = os.path.join("/tmp", name)
    with open(local, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=2, ensure_ascii=False)
    ssh('if not exist %s mkdir %s' % (STAGING, STAGING))
    cp = subprocess.run(["scp", "-o", "ConnectTimeout=25", local,
                         "%s:%s/%s" % (SSH_HOST, STAGING.replace("\\", "/"), name)],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", timeout=120)
    if cp.returncode:
        sys.exit("!! scp failed: %s" % (cp.stderr or cp.stdout))
    # move, not copy: the runner claims by renaming out of ready/, so a file
    # must never be visible there while it is still being written. The same
    # reasoning covers backlog/ -- box_autofill.py files by renaming out of it.
    ssh('if not exist %s\\%s mkdir %s\\%s' % (QUEUE_ROOT, dest, QUEUE_ROOT, dest))
    mv = ssh('move /Y %s\\%s %s\\%s\\%s' % (STAGING, name, QUEUE_ROOT, dest, name))
    if mv.returncode:
        sys.exit("!! move into %s/ failed: %s" % (dest, mv.stderr or mv.stdout))
    print("  %s %s" % ("backlogged" if dest == "backlog" else "queued", name))


def known_harnesses() -> list:
    """Every --harness any spec in pipeline/jobs names, deduped, sorted.

    Read off the specs rather than off a list in this file, and off the specs
    rather than off the box's directory listing. A list here would be one more
    copy to keep fresh -- which is the bug. And the box's listing is the wrong
    set in both directions: it holds harnesses no spec uses (scratch) and it
    would happily accept a new harness that no spec has ever named.
    """
    out = set()
    for name in sorted(os.listdir(JOBS_DIR)):
        if not name.endswith((".yaml", ".json")):
            continue
        try:
            spec = load_spec(os.path.join(JOBS_DIR, name))
        except Exception:
            continue
        if isinstance(spec, dict):
            out.update(spec_harnesses(spec))
    return sorted(out)


def sync_drafts(dry_run: bool = False) -> int:
    """Copy pipeline/wave-drafts.yaml over every harness copy on the box.

    THE REMEDY THE REFUSAL NAMES. A guard whose message ends at "this is wrong"
    gets switched off -- the runner watchdog was off for four days after exactly
    that -- so harness_drafts_problems names this command and this command has
    to work without further thought.

    IT REFUSES WHILE THE QUEUE IS BUSY, and that is not politeness. The renderer
    opens the drafts file at run time, and its `--dry` preflight and its sample
    step open it SEPARATELY, minutes apart. Overwriting between the two would
    hand one job two different wordings and record the second one's hash for
    both. So: nothing in ready/ or running/, or nothing happens.
    """
    repo_sha = file_sha256(REPO_DRAFTS)
    print("repo pipeline/wave-drafts.yaml  %s" % repo_sha)

    ids, why = queued_job_ids()
    if ids is None:
        print("!! could not read the box queue (%s) -- refusing to swap a file "
              "the renderer may have open" % why)
        return 3
    busy = ssh('dir /b %s\\ready\\*.json 2>nul & dir /b %s\\running\\*.json 2>nul'
               % (QUEUE_ROOT, QUEUE_ROOT))
    live = [l for l in (busy.stdout or "").splitlines() if l.strip()]
    if live and not dry_run:
        print("!! %d job(s) in ready/ or running/ -- NOT swapping the drafts "
              "file under a job that may be mid-read.\n"
              "   Re-run when the queue is drained, or sync the one harness "
              "the running job is not using, by hand." % len(live))
        return 4

    targets = known_harnesses()
    if not targets:
        print("no spec names a --harness; nothing to sync")
        return 0
    rc = 0
    for harness in targets:
        path = harness + "\\wave-drafts.yaml"
        theirs = box_file_sha256(path)
        if theirs == repo_sha:
            print("  ok      %s" % path)
            continue
        print("  STALE   %s  %s" % (path, theirs or "(unreadable)"))
        if dry_run:
            rc = 1
            continue
        # encoding named for ssh()'s reason: scp's errors come back through the
        # same cp1252 shell, and a locale decode failure silently blanks stderr.
        cp = subprocess.run(["scp", "-q", REPO_DRAFTS,
                             "%s:%s" % (SSH_HOST, path.replace("\\", "/"))],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=300)
        if cp.returncode != 0:
            print("  !! scp failed: %s" % (cp.stderr or "").strip())
            rc = 5
            continue
        after = box_file_sha256(path)
        if after != repo_sha:
            print("  !! copied and it STILL does not match (%s) -- say so "
                  "rather than assume" % after)
            rc = 6
        else:
            print("  synced  %s  -> %s" % (path, repo_sha))
    return rc


def show_queue() -> int:
    r = ssh('echo [ready] & dir /b %s\\ready 2>nul & echo [running] & '
            'dir /b %s\\running 2>nul & echo [backlog] & dir /b %s\\backlog 2>nul & '
            'echo [done] & dir /b %s\\done\\*.json 2>nul & '
            'echo [failed] & dir /b %s\\failed\\*.json 2>nul'
            % (QUEUE_ROOT, QUEUE_ROOT, QUEUE_ROOT, QUEUE_ROOT, QUEUE_ROOT))
    sys.stdout.write(r.stdout)
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    return r.returncode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="enqueue a job on the rtx5090 box queue")
    ap.add_argument("spec", nargs="*", help="pipeline/jobs/<id>.yaml")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate and print the job json, touch nothing")
    ap.add_argument("--list", action="store_true", help="show the box queue and exit")
    ap.add_argument("--sync-drafts", action="store_true",
                    help="copy pipeline/wave-drafts.yaml over every harness copy on "
                         "the box, then exit. The remedy named by the STALE DRAFTS "
                         "refusal. Refuses while ready/ or running/ is non-empty")
    ap.add_argument("--check-drafts", action="store_true",
                    help="report every harness copy's sha256 against ours and exit "
                         "without writing anything; nonzero when any has drifted")
    ap.add_argument("--backlog", action="store_true",
                    help="file into backlog/ instead of ready/: same guards, but the "
                         "job waits there until box_autofill.py finds the card hungry")
    ap.add_argument("--again", action="store_true",
                    help="file a job the box has already run: prints every refusal "
                         "it is overriding and mints a fresh id token, so the new "
                         "record cannot land on the old one")
    ap.add_argument("--expires-h", type=float, default=36.0,
                    help="hours a backlog entry stays true; past it the autofill "
                         "parks it .EXPIRED rather than firing a stale recipe")
    args = ap.parse_args(argv)

    if args.list:
        return show_queue()
    if args.check_drafts:
        return sync_drafts(dry_run=True)
    if args.sync_drafts:
        return sync_drafts()
    if not args.spec:
        ap.error("give at least one spec, or --list")

    # What the box has queued right now, read ONCE. A real enqueue may not
    # proceed without it: writing payloads while unable to check whose paths
    # they are is the failure this guard exists for, and "the check could not
    # run" is not a pass. A dry run stays usable off the network -- it writes
    # nothing -- and says out loud that it only checked the grace window.
    live_ids = None
    if args.dry_run:
        print("(dry run: box queue not read -- collision check covers only "
              "enqueues from the last %ds, and done/ is not consulted at all, "
              "so a dry run cannot tell you whether this job already ran)"
              % RESERVE_GRACE_SEC)
    else:
        live_ids, why = queued_job_ids()
        if live_ids is None:
            sys.exit("!! cannot read the box queue (%s) -- the payload collision "
                     "guard cannot run, so nothing was sent or queued" % why)

    failures = 0
    # A dry run writes no reservation, so specs named together on one command
    # line would not see each other -- and checking a pair before sending it is
    # the whole reason to dry-run a pair. These stand in for the index lines a
    # real run would have written.
    pending = []
    for path in args.spec:
        print("%s" % path)
        spec = load_spec(path)
        job = to_job(spec, again=args.again)
        if args.backlog:
            job = with_backlog_meta(job, path, args.expires_h)
        # The sha rides along on the job whatever happens next -- the NEXT
        # filing is what reads it back off the record.
        job = with_run_sha(job, spec.get("payload"))
        # Printed rather than left in the json, which --dry-run truncates at
        # 2000 characters and this key is appended past: it is what the next
        # filing compares against, so it is the one number a person re-filing
        # by hand needs to be able to read and grep for.
        print("  sha      %s  (spec_sha256)" % job["spec_sha256"])
        # Asked before the gates, because it is the one question whose answer
        # makes every other check moot: has the card already done exactly this?
        # A dry run cannot ask it (it reads nothing off the box) and says so.
        problems = []
        if not args.dry_run:
            found, why = prior_runs(base_job_id(job["id"]), job["spec_sha256"])
            if found is None:
                sys.exit("!! cannot read the box's done/ and failed/ (%s) -- the "
                         "already-ran guard cannot run, so nothing was sent or "
                         "queued" % why)
            dups = duplicate_problems(job, job["spec_sha256"], found,
                                      live_ids=live_ids, spec_path=path)
            dups, overridden = dup_override(dups, args.again, job["id"])
            for note in overridden:
                print("  %s" % note)
            problems += dups
        problems += gate_checks(spec, job)
        if args.backlog:
            problems += backlog_problems(spec)
        # rid identifies THIS claim, so the re-read below can tell our own line
        # from a peer's. pid+ns is unique across lanes on one machine.
        mine = {"rid": "%d-%d" % (os.getpid(), time.time_ns()),
                "job": job["id"], "ts": time.time(), "spec": path,
                "dests": payload_dests(spec)}
        problems += payload_collisions(mine, read_payload_index() + pending,
                                       live_ids, mine["ts"])
        if problems:
            for p in problems:
                print("  !! %s" % p)
            failures += 1
            continue
        # LAST, after every check has run against the argv the author wrote: the
        # filing-time drafts hash goes into the job's own command line so the
        # renderer can re-check it hours later. Deliberately after validation
        # (nothing downstream re-reads the spec's argv, so the two cannot drift
        # into disagreeing) and deliberately before the dry-run print, so
        # --dry-run shows exactly what would be queued.
        job, drafts_notes = inject_drafts_expectation(job, spec)
        for note in drafts_notes:
            print("  drafts  %s" % note)
        if args.dry_run:
            pending.append(mine)
            for dest in (spec.get("payload") or {}):
                print("  would send payload -> %s" % dest)
            print(json.dumps(job, indent=2)[:2000])
            print("  (dry run -- not queued)")
            continue
        if mine["dests"]:
            # Claim, then re-read: a peer lane that appended between our check and
            # our claim is only visible on the second look, and one of the two has
            # to lose. Still nothing written to the box at this point.
            reserve_payload(mine)
            problems = payload_collisions(mine, read_payload_index(), live_ids, mine["ts"])
            if problems:
                for p in problems:
                    print("  !! %s" % p)
                failures += 1
                continue
        send_payload(spec.get("payload"))
        enqueue(job, dest="backlog" if args.backlog else "ready")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
