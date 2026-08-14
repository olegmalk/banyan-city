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

    python3 pipeline/box_enqueue.py pipeline/jobs/<spec>.yaml [--dry-run]
    python3 pipeline/box_enqueue.py --list        # what is queued right now
"""

from __future__ import annotations

import argparse
import json
import os
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
# THE UNFETCHABLE REFUSAL IS THE PART THAT HAS NOT FAILED, and it earned its
# keep on its first outing: it caught a silently-swapped plate whose path was
# built from the new beat's directory and the old beat's filename. "I could not
# check" must keep exiting nonzero whatever happens to the border statistic.
RESULTS_BRANCH = "origin/farm-results-rtx5090"
BOX_OUT_PREFIX = "c:\\banyan-farm\\courier-box\\farm-out\\"
PLATE_FLAT_MAX = 0.62      # midpoint of the 0.489 -> 0.750 gap; see above
PLATE_BAND = 0.08          # outer fraction of the short side sampled as "border"
PLATE_TOL = 8              # luminance levels either side of the border median
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


def measure_plate(blob: bytes) -> float:
    """Flatness of an image's bytes, cropped as the box crops it."""
    import io

    from PIL import Image

    return border_flatness(cover_crop(Image.open(io.BytesIO(blob))))


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
    ack = str(spec.get("plate_ack") or "").strip()
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
        if ack.lower().startswith("unfetchable"):
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
        if ack.lower().startswith("unfetchable"):
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
    if ack.lower().startswith("card"):
        print("  plate    flatness %.3f of %.2f reads as a CARD, waived by the spec "
              "-- %s" % (flat, PLATE_FLAT_MAX, ack))
        return []
    return ["BLOCKED: the picture this job would animate looks like a CHARACTER CARD, "
            "not a scene -- a figure on flat blank paper with no location.\n"
            "      border flatness %.3f, and %.2f or above is blank paper\n"
            "      --src %s\n"
            "      Point the job at a real scene plate and enqueue it again. Do not "
            "just re-run it: an animated reference sheet is worthless footage that "
            "still scores near the TOP on frame-difference, which is how six of these "
            "got past everything on 2026-08-14. If it really is a deliberate macro or "
            "close-up, say so in the spec: plate_ack: \"card: <why>\"."
            % (flat, PLATE_FLAT_MAX, src)]


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
    problems += plate_problems(spec)
    return problems


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
    """(ids, None) for what is in ready/ and running/, or (None, why-not)."""
    r = ssh('dir /b %s\\ready\\*.json 2>nul & dir /b %s\\running\\*.json 2>nul & '
            'echo %s' % (QUEUE_ROOT, QUEUE_ROOT, QUEUE_MARKER))
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


def enqueue(job: dict) -> None:
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
    # must never be visible there while it is still being written.
    mv = ssh('move /Y %s\\%s %s\\ready\\%s' % (STAGING, name, QUEUE_ROOT, name))
    if mv.returncode:
        sys.exit("!! move into ready/ failed: %s" % (mv.stderr or mv.stdout))
    print("  queued %s" % name)


def show_queue() -> int:
    r = ssh('echo [ready] & dir /b %s\\ready 2>nul & echo [running] & '
            'dir /b %s\\running 2>nul & echo [done] & dir /b %s\\done\\*.json 2>nul & '
            'echo [failed] & dir /b %s\\failed\\*.json 2>nul'
            % (QUEUE_ROOT, QUEUE_ROOT, QUEUE_ROOT, QUEUE_ROOT))
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
        problems = gate_checks(spec, job)
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
        enqueue(job)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
