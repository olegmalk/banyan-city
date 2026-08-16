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
"""

from __future__ import annotations

import argparse
import json
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


def to_job(spec: dict) -> dict:
    """Spec (repo vocabulary) -> job (what box_runner executes).

    Only the keys the runner reads are copied through. Everything else in a spec
    -- consumer, success, why, gate -- is planning metadata that stays in the
    repo file, where a person reads it, rather than riding to the box as noise.
    """
    jid = spec.get("id")
    if not jid:
        sys.exit("!! spec has no id")
    if spec.get("stamp_id", True) and not jid[-10:].isdigit():
        jid = "%s-%d" % (jid, int(time.time()))
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


def enqueue(job: dict, dest: str = "ready") -> None:
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
    ap.add_argument("--backlog", action="store_true",
                    help="file into backlog/ instead of ready/: same guards, but the "
                         "job waits there until box_autofill.py finds the card hungry")
    ap.add_argument("--expires-h", type=float, default=36.0,
                    help="hours a backlog entry stays true; past it the autofill "
                         "parks it .EXPIRED rather than firing a stale recipe")
    args = ap.parse_args(argv)

    if args.list:
        return show_queue()
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
              "enqueues from the last %ds)" % RESERVE_GRACE_SEC)
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
        job = to_job(spec)
        if args.backlog:
            job = with_backlog_meta(job, path, args.expires_h)
        problems = gate_checks(spec, job)
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
