#!/usr/bin/env python3
r"""Put a rendered clip on the beats page as a CANDIDATE, with its provenance.

    python3 pipeline/stage_candidate.py farm-out/<job>/<clip>.mp4
    python3 pipeline/stage_candidate.py farm-out/<job>/<clip>.mp4 --poster-frame 40
    python3 pipeline/stage_candidate.py --check          # audit what is staged

WHY THIS IS A SCRIPT. Staging a candidate is four steps that must all happen or
none of them should: copy the mp4 into `review/ep2-beats-0821/candidates/`, copy
its `.meta.yaml` sidecar beside it, cut a poster jpg under `posters/` with the
EXACT basename the page will ask for, and confirm the page can actually reach
all three. Done by hand it is four `cp`s, and the failure mode is silent and
specific: `review/**/*.png|jpg|mp4` are gitignored while `.meta.yaml` is NOT, so
a forgotten sidecar is invisible locally and a forgotten POSTER is invisible
everywhere until the founder opens the page and sees a black rectangle. That has
a name in this tree -- QA BEFORE HANDOVER -- and this is that rule as code.

WHAT IT REFUSES:
  * a clip with no `.meta.yaml` beside it. A candidate without provenance is
    not publishable under 7.2, and the sidecar is the only record of what the
    render WAS.
  * a poster that ffmpeg did not actually write, or wrote empty.
  * a `--poster-frame` past the end of the clip. ffmpeg is happy to select
    nothing and exit 0, which is how you get a zero-byte jpg and a page that
    looks broken only to the person you handed it to.

IT DOES NOT WRITE THE PAGE. `review/ep2-beats-0821/build_page.py` holds an
authored line per candidate -- a label, a verdict and a diff -- and those are
sentences somebody has to write after LOOKING at the clip. A script that
invented them would be the exact thing the page exists to prevent.
"""
import argparse
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(REPO, "review", "ep2-beats-0821")
CAND = os.path.join(PAGE, "candidates")
POST = os.path.join(PAGE, "posters")


def _run(argv):
    return subprocess.run(argv, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def frame_count(path):
    r = _run(["ffprobe", "-v", "error", "-select_streams", "v:0",
              "-show_entries", "stream=nb_frames", "-of",
              "default=nw=1:nk=1", path])
    try:
        return int((r.stdout or "").strip())
    except ValueError:
        return None


def stage(clip_rel, poster_frame=0):
    src = os.path.join(REPO, clip_rel)
    if not os.path.isfile(src):
        raise SystemExit("!! %s is not a file" % clip_rel)
    name = os.path.basename(src)
    meta_src = src + ".meta.yaml"
    if not os.path.isfile(meta_src):
        raise SystemExit("!! %s has no .meta.yaml beside it. A candidate "
                         "without provenance is not publishable (7.2), and the "
                         "sidecar is the only record of what the render was."
                         % name)

    n = frame_count(src)
    if n is not None and poster_frame >= n:
        raise SystemExit("!! --poster-frame %d is past the end of a %d-frame "
                         "clip. ffmpeg would select nothing, exit 0 and leave "
                         "an empty jpg." % (poster_frame, n))

    os.makedirs(CAND, exist_ok=True)
    os.makedirs(POST, exist_ok=True)
    shutil.copy2(src, os.path.join(CAND, name))
    shutil.copy2(meta_src, os.path.join(CAND, name + ".meta.yaml"))

    poster = os.path.join(POST, os.path.splitext(name)[0] + ".jpg")
    r = _run(["ffmpeg", "-v", "error", "-i", src, "-vf",
              "select=eq(n\\,%d)" % poster_frame, "-frames:v", "1",
              "-q:v", "3", "-y", poster])
    if r.returncode or not os.path.exists(poster) or \
            os.path.getsize(poster) == 0:
        raise SystemExit("!! poster not written for %s: %s"
                         % (name, (r.stderr or "empty file").strip()[:300]))

    print("staged %s" % name)
    print("   clip   review/ep2-beats-0821/candidates/%s" % name)
    print("   meta   review/ep2-beats-0821/candidates/%s.meta.yaml" % name)
    print("   poster review/ep2-beats-0821/posters/%s  (frame %d of %s)"
          % (os.path.basename(poster), poster_frame, n))
    print("   NOW WRITE ITS LINE in review/ep2-beats-0821/build_page.py --")
    print("   label, verdict and diff, after looking at the clip.")
    return name


def check():
    """Every candidate mp4 the page could show, and what it is missing."""
    bad = 0
    for name in sorted(os.listdir(CAND)):
        if not name.endswith(".mp4"):
            continue
        miss = []
        if not os.path.exists(os.path.join(CAND, name + ".meta.yaml")):
            miss.append("meta")
        p = os.path.join(POST, os.path.splitext(name)[0] + ".jpg")
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            miss.append("poster")
        if miss:
            bad += 1
            print("MISSING %-8s %s" % (",".join(miss), name))
    print("%d candidate mp4(s) incomplete" % bad)
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clips", nargs="*")
    ap.add_argument("--poster-frame", type=int, default=0)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    if a.check:
        return check()
    if not a.clips:
        ap.error("pass one or more clip paths, or --check")
    for c in a.clips:
        stage(c, a.poster_frame)
    return 0


if __name__ == "__main__":
    sys.exit(main())
