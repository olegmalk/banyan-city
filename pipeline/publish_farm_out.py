#!/usr/bin/env python3
"""Copy a job's rendered output into courier-box/farm-out, or FAIL LOUDLY.

WHY THIS FILE EXISTS (2026-08-17, sixty images)
-----------------------------------------------
Every box job spec hand-rolls its own publish step as a one-line inline python
string, and they are all the same six lines:

    src = sorted(glob.glob(OUT + "/12-wave1-s*.*"))
    for f in src: shutil.copy2(f, dst)
    ... write dst/<job>.sha256 ...
    raise SystemExit(0 if len(src) == 8 else 1)

Read what that does when the glob matches NOTHING. `src` is `[]`. The copy loop
does not run. The manifest is still opened, still written, and contains zero
lines. It prints "published 0 file(s) + manifest". A directory appears in
farm-out holding one empty manifest and no pixels, and it looks exactly like a
published set.

That is what happened to beats 12, 18 and 21 on 2026-08-14: the glob said
`12-wave1-s*` and the sampler had written `12-related-wave1-s*` -- the beat SLUG
again, the same missing segment that broke the artifact declarations (see THE RC
TABLE in box_runner.py, and resolve_artifact there). Three jobs rendered
correctly, published nothing, wrote three empty manifests, and were retired
FAILED. The frames were rescued by hand 44 minutes later and then sat
uncommitted for three days, because the only record of them was a `failed/`
entry.

The count assertion at the end is not the guard people think it is. It fires
AFTER the manifest is on disk, so the empty manifest survives the failure; and
specs that carry `allow_fail: true` on their publish step -- most of them do,
so a bad copy never marks a good render failed -- discard its exit code
entirely. A zero-match glob was therefore a silent, green, permanent no-op.

THE RULE HERE: a source pattern that matches zero files is an ERROR, and no
manifest is written unless files were actually copied. Nothing is published
optimistically and corrected later; there is no "later".

This is the third instance of one shape found on 2026-08-17 -- a canon guard
passing green while checking nothing, a runner reporting `State: Running` while
dead, and a publish step reporting success while copying nothing. The question
that separates a check from a decoration is the one test_silent_gates.py asks:
WHAT WOULD THIS PRINT IF THE THING IT READS WERE COMPLETELY BROKEN?

WHAT IT DOES NOT DO
-------------------
It does not guess. When the literal pattern matches nothing, it retries with the
beat slug wildcarded in and, if that finds files, NAMES THEM IN THE ERROR --
then still fails. The runner resolves a slug-dropped *declaration* because by
then the pixels are on disk and the alternative is re-rendering; a publish step
has no such excuse, because the spec that is about to be re-read is right there
and the fix is one line. Substituting here would only teach the next spec that
the slug is optional, which is how six of these were written.

Usage (from a job spec's publish step -- argv, not inline python):

    python pipeline/publish_farm_out.py
        --dst C:/banyan-farm/courier-box/farm-out/ep2-b12-scene-0814
        --src "C:/banyan-farm/wave-goblin-prep/out-b12-scene/12-related-wave1-s*.*"
        --expect 8

Exit codes come from box_runner's RC TABLE and are defined nowhere else:
  0   files copied, count matched, manifest written
  95  RC_PUBLISHED_NOTHING -- a pattern matched zero files, or every pattern did
  92  RC_ARTIFACTS_MISSING -- files copied but not as many as --expect
  2   the invocation itself is wrong (no --src, unwritable --dst)
"""

import argparse
import glob
import hashlib
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from box_runner import RC_ARTIFACTS_MISSING, RC_PUBLISHED_NOTHING  # noqa: E402

# `12-related-wave1-s0.png` is what the sampler writes; a spec cloned from a
# template predating the slug says `12-wave1-s0.png`. Same beat number, same
# tail, one missing segment between them. Kept deliberately identical in intent
# to box_runner._BEAT_STEM.
_BEAT_STEM = re.compile(r"^(\d{1,3})-(.+)$")


def slug_variant(pattern: str):
    """The same pattern with the beat slug wildcarded in, or None.

    `out/12-wave1-s*.*` -> `out/12-*-wave1-s*.*`. Used ONLY to explain a
    zero-match failure, never to publish.
    """
    base = os.path.basename(pattern)
    m = _BEAT_STEM.match(base)
    if not m:
        return None
    return os.path.join(os.path.dirname(pattern), "%s-*-%s" % (m.group(1), m.group(2)))


def what_is_there(pattern: str, limit: int = 12) -> str:
    """The listing of the directory the pattern points at.

    "matched 0 files" is the half of the comparison nobody needs; the question
    is always "then what DID the sampler write?". Answering it used to take an
    ssh session.
    """
    d = os.path.dirname(pattern) or "."
    if not os.path.isdir(d):
        return "%s -- the directory does not exist" % d
    names = sorted(os.listdir(d))
    if not names:
        return "%s -- exists and is EMPTY" % d
    return "%s -- %d file(s): %s%s" % (
        d, len(names), ", ".join(names[:limit]), " ..." if len(names) > limit else "")


def resolve_sources(patterns):
    """(files, faults). A pattern matching zero files is a fault, always."""
    files, faults = [], []
    for pattern in patterns:
        hits = sorted(p for p in glob.glob(pattern) if os.path.isfile(p))
        if hits:
            files.extend(hits)
            continue
        lines = ["!! PUBLISHED NOTHING: source pattern matched 0 files",
                 "   pattern: %s" % pattern,
                 "   %s" % what_is_there(pattern)]
        alt = slug_variant(pattern)
        if alt and alt != pattern:
            near = sorted(p for p in glob.glob(alt) if os.path.isfile(p))
            if near:
                lines.append(
                    "   the beat SLUG is missing from the pattern: %s matches "
                    "%d file(s) (%s). FIX THE SPEC -- not publishing a guess."
                    % (alt, len(near),
                       ", ".join(os.path.basename(p) for p in near[:4])))
        faults.append("\n".join(lines))
    # de-duplicate while keeping order: two patterns may overlap
    seen, out = set(), []
    for f in files:
        key = os.path.normcase(os.path.abspath(f))
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out, faults


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def publish(dst: str, patterns, expect=None, manifest_name=None, out=sys.stdout) -> int:
    """Copy every match into dst and write the manifest. See module docstring."""
    files, faults = resolve_sources(patterns)

    # Order matters: refuse BEFORE anything is written. The defect this replaces
    # wrote its manifest first and asserted afterwards, so the empty manifest
    # outlived the failure.
    if faults:
        for f in faults:
            out.write(f + "\n")
        out.write("!! refusing to write a manifest for 0 published files "
                  "(rc=%d RC_PUBLISHED_NOTHING)\n" % RC_PUBLISHED_NOTHING)
        return RC_PUBLISHED_NOTHING

    if expect is not None and len(files) != expect:
        out.write("!! declared --expect %d, the pattern(s) matched %d: %s\n"
                  % (expect, len(files),
                     ", ".join(os.path.basename(f) for f in files[:8])))
        out.write("!! refusing to write a manifest for a partial set "
                  "(rc=%d RC_ARTIFACTS_MISSING)\n" % RC_ARTIFACTS_MISSING)
        return RC_ARTIFACTS_MISSING

    os.makedirs(dst, exist_ok=True)
    name = manifest_name or (os.path.basename(dst.rstrip("/\\")) + ".sha256")
    lines = []
    for src in files:
        shutil.copy2(src, dst)
        landed = os.path.join(dst, os.path.basename(src))
        # Hash what LANDED, not what was read. A copy that truncates is exactly
        # the failure a manifest is supposed to catch, and hashing the source
        # would attest to a file nobody will ever open again.
        lines.append("%s  %s" % (sha256_of(landed), os.path.basename(src)))

    with open(os.path.join(dst, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    out.write("published %d file(s) + %s -> %s\n" % (len(files), name, dst))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="publish a job's output to farm-out, or fail loudly")
    ap.add_argument("--dst", required=True, help="farm-out directory for this job")
    ap.add_argument("--src", action="append", default=[], metavar="GLOB",
                    help="source glob; repeatable. Zero matches is an error.")
    ap.add_argument("--expect", type=int, default=None,
                    help="how many files the spec says should land")
    ap.add_argument("--manifest", default=None,
                    help="manifest filename (default: <dst basename>.sha256)")
    args = ap.parse_args(argv)
    if not args.src:
        sys.stderr.write("!! no --src given: a publish step with no source "
                         "pattern would publish nothing and say it worked\n")
        return 2
    return publish(args.dst, args.src, expect=args.expect,
                   manifest_name=args.manifest)


if __name__ == "__main__":
    sys.exit(main())
