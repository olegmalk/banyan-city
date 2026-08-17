#!/usr/bin/env python3
r"""Are the box's published results real, complete, and visible to `main`?

WHY THIS FILE EXISTS (2026-08-17, eleven stranded sets)
-------------------------------------------------------
`C:\banyan-farm\courier-box` is a git clone on branch `farm-results-rtx5090`,
and the runner commits and pushes a job's results into it. Nothing merges that
branch to `main`. The chain

    sampler -> publish -> commit -> push origin/farm-results-rtx5090 -> (nothing)

has no last link, and the leak is invisible because EVERY question anyone asks is
asked of `main`: `git ls-files`, the site build, `build_shotboard.py`, the review
pages, every triage. A set sitting on the results branch answers "does this
exist?" with **no**, in exactly the same voice as a set that was never rendered.

On 2026-08-17 a triage ran `git ls-files farm-out/<job>` for six sets, got 0 for
all six, and concluded they existed in exactly one place and were one disk
failure from gone. They had been on origin since 08-14. This file is the check
that was missing. It does not close the leak -- see
`farm-branch-merge-gap-0817.md` for why an auto-merging courier is a design
decision above a lane (the same push deploys the site).

WHAT THIS FILE DOES NOT ASSERT, AND WHY (measured, 2026-08-17)
--------------------------------------------------------------
The obvious invariant -- "every path on the results branch should be in `main`,
and the count should always be zero" -- is FALSE HERE, and shipping it as a gate
would have been a third decoration. Measured:

    results branch   716 job dirs, 8850 paths absent from main
    main               26 job dirs

`main` holds a curated subset **on purpose**: `.gitignore` records the policy in
so many words -- "Media does not go into git; only the frame the founder picks
does, promoted deliberately". The branch is every take ever rendered. A gate that
reads 8850 is exactly as useless as a gate that reads 0 always: nobody reads it
either way. Its twin, "any rc=0 job whose published dir is not in main is a leak
by definition", measures **1095 violations across 776 jobs** for the same reason.

So the raw divergence is reported as a NUMBER WITH ITS REASON and never gates.
What gates is what can honestly be zero:

  GATE 1 -- no published set may be EMPTY or internally inconsistent.
      A `.sha256` manifest with no lines, or a line count that disagrees with the
      file count, means the publish step attested to something it did not copy.
      Measured across all 716 dirs: 697 consistent, 0 mismatched, **1 empty** --
      `ep2-b01-final055-r2`, whose publish globbed a directory that does not
      exist, "published 0 file(s) + manifest", and wrote the empty manifest
      anyway. That is the defect `publish_farm_out.py` now refuses at source.
      One known instance is a gate that can reach zero and stay there.

  GATE 2 -- a `failed/` entry must not own a complete attested set.
      If the board says a job failed and the results branch holds a complete,
      manifest-consistent set under the directory that job publishes to, then the
      board is wrong about what is filmed. This is precisely the eleven-set
      defect, and it is a bounded worklist that shrinks as each entry is looked
      at or merged -- unlike the 8850, which is structural.

"COULD NOT CHECK" IS NOT "FINE"
-------------------------------
The failure class this file guards against is a check that reads nothing and
reports health, so every unreadable input is LOUD and nonzero:

- an unreadable ref (the results branch is not fetched in CI, which clones one
  branch) exits RC_CANNOT_CHECK and prints the fetch command. It does NOT pass.
- a `done/`/`failed/` directory that cannot be read is reported as SKIPPED IN
  WORDS. A half that did not run must never look like a half that found nothing.

Run:
    python3 pipeline/check_results_merged.py
    python3 pipeline/check_results_merged.py --main-ref 5f4cdb2a   # before the recovery
    python3 pipeline/check_results_merged.py --queue-dir C:\banyan-queue
"""

import argparse
import collections
import glob
import json
import os
import re
import subprocess
import sys

RESULTS_REF = "origin/farm-results-rtx5090"
FARM_OUT = "farm-out"

RC_OK = 0
RC_STRANDED = 1
RC_CANNOT_CHECK = 2

# Only a publish step's DESTINATION counts. Matching `courier-box/farm-out/...`
# anywhere in the job json also catches paths a job READS -- motion-poscontrol
# reads ep2-b13-plate-0814's plates -- and calling that job's own output is how a
# check starts reporting other people's directories as its leaks.
_PUBLISH_DST = re.compile(
    r"""dst\s*=\s*["'][^"']*courier-box[\\/]+farm-out[\\/]+([A-Za-z0-9._-]+)""")

def is_manifest(path: str) -> bool:
    """Both spellings the specs use, because assuming one was wrong (2026-08-17).

    Most publish steps write `<job-id>.sha256`; a newer family writes
    `SHA256SUMS.txt`. The first version of this check knew only the first
    spelling and reported seven of today's perfectly-attested sets as "no
    manifest at all" -- including `ep2-b10-attrbind-eyewear-0817b`, which hashes
    every file it copies. That is this file's own recurring failure mode wearing a
    third mask: a check reporting the absence of the thing when what is absent is
    its own knowledge of the thing. If a fourth naming appears, it belongs here,
    not in an allowlist of directories to forgive.
    """
    name = os.path.basename(path)
    return name.endswith(".sha256") or name.upper() == "SHA256SUMS.TXT"


class CannotCheck(Exception):
    """An input could not be read. Never downgraded to a pass."""


def git_out(args, repo=None, binary=False, stdin=None):
    cmd = ["git"] + (["-C", repo] if repo else []) + list(args)
    p = subprocess.run(cmd, capture_output=True, input=stdin)
    if p.returncode != 0:
        raise CannotCheck("`%s` failed rc=%d: %s"
                          % (" ".join(cmd), p.returncode,
                             p.stderr.decode("utf-8", "replace").strip()[:200]))
    return p.stdout if binary else p.stdout.decode("utf-8", "replace")


def farm_out_paths(ref, repo=None) -> set:
    """Every path under farm-out/ at `ref`. Raises CannotCheck if ref is unreadable."""
    try:
        out = git_out(["ls-tree", "-r", "--name-only", ref, "--", FARM_OUT], repo)
    except CannotCheck as exc:
        raise CannotCheck(
            "%s\n   cannot read `%s`. In CI or a fresh clone the results branch is "
            "not fetched:\n     git fetch --depth=1 origin "
            "farm-results-rtx5090:refs/remotes/origin/farm-results-rtx5090\n"
            "   NOT passing: the branch this check cannot read is the one place "
            "the leak hides." % (exc, ref))
    return {ln for ln in out.split("\n") if ln.strip()}


def job_dir_of(path: str):
    """`farm-out/ep2-b05-scene-0814/05-...png` -> `ep2-b05-scene-0814`."""
    parts = path.split("/")
    return parts[1] if len(parts) > 2 and parts[0] == FARM_OUT else None


def group_by_dir(paths) -> dict:
    out = collections.defaultdict(list)
    for p in paths:
        d = job_dir_of(p)
        if d:
            out[d].append(p)
    return dict(out)


def read_blobs(ref, paths, repo=None) -> dict:
    """{path: text} for many blobs in one `git cat-file --batch`."""
    paths = list(paths)
    if not paths:
        return {}
    req = "".join("%s:%s\n" % (ref, p) for p in paths).encode()
    buf = git_out(["cat-file", "--batch"], repo, binary=True, stdin=req)
    out, i = {}, 0
    for p in paths:
        nl = buf.find(b"\n", i)
        if nl < 0:
            break
        header = buf[i:nl].decode("utf-8", "replace")
        if "blob" not in header:          # missing object; skip its record
            i = nl + 1
            out[p] = ""
            continue
        size = int(header.split()[-1])
        out[p] = buf[nl + 1:nl + 1 + size].decode("utf-8", "replace")
        i = nl + 1 + size + 1
    return out


def set_shape(ref, by_dir, repo=None):
    """{dir: (n_files, n_manifest_lines, n_manifests)} for every set at `ref`."""
    mans = {d: sorted(p for p in ps if is_manifest(p))
            for d, ps in by_dir.items()}
    blobs = read_blobs(ref, [m[0] for m in mans.values() if len(m) == 1], repo)
    shape = {}
    for d, ps in by_dir.items():
        m = mans[d]
        files = [p for p in ps if not is_manifest(p)]
        lines = ([l for l in blobs.get(m[0], "").split("\n") if l.strip()]
                 if len(m) == 1 else [])
        shape[d] = (len(files), len(lines), len(m))
    return shape


def unattested_sets(ref=RESULTS_REF, repo=None):
    """CONTEXT, not a gate. Dirs with files and no manifest of any spelling.

    This was a gate for one revision and it was wrong twice over. First it fired
    on seven attested sets because it did not know `SHA256SUMS.txt` (see
    `is_manifest`). Then, with that fixed, what remains are hand-assembled rescue
    directories and the queue's own mirror -- sets nobody published through a job,
    which have no manifest because no publish step ever ran, not because one lied.
    Keeping it as a gate needed a hand-maintained allowlist of directories to
    forgive, and an allowlist that must be edited every time the branch grows is a
    gate waiting to become decoration. An unattested set is a weaker claim than a
    lying manifest, so it is reported as a number and does not decide the rc.
    """
    by_dir = group_by_dir(farm_out_paths(ref, repo))
    return sorted(d for d, (f, l, n) in set_shape(ref, by_dir, repo).items()
                  if n == 0 and f)


def inconsistent_sets(ref=RESULTS_REF, repo=None):
    """GATE 1. [(dir, why, n_files, n_lines)] for manifests that lie.

    Only sets that HAVE a manifest are judged, because only a manifest can be
    wrong. Empty and count-mismatched are the two ways a publish step attests to
    something it never copied, which is the defect `publish_farm_out.py` refuses
    at source.
    """
    by_dir = group_by_dir(farm_out_paths(ref, repo))
    bad = []
    for d, (files, lines, n_man) in sorted(set_shape(ref, by_dir, repo).items()):
        if n_man == 0:
            continue                      # unattested: reported, never a verdict
        if n_man > 1:
            continue                      # ambiguity, reported separately
        if files == 0 or lines == 0:
            bad.append((d, "EMPTY -- attested to nothing", files, lines))
        elif files != lines:
            bad.append((d, "manifest disagrees with the directory", files, lines))
    return bad


def complete_sets(ref=RESULTS_REF, repo=None) -> set:
    by_dir = group_by_dir(farm_out_paths(ref, repo))
    return {d for d, (f, l, n) in set_shape(ref, by_dir, repo).items()
            if n == 1 and f > 0 and f == l}


def _strings_in(obj):
    """Every string anywhere in a job record, unescaped.

    NOT `json.dumps(job)`: dumping re-escapes the inline python a publish step
    carries, so `dst = "C:/..."` becomes `dst = \\"C:/...` and a regex anchored on
    the quote silently matches nothing. That produced a green gate 2 on a tree
    known to hold eight stranded sets -- the exact failure this file exists to
    catch, found by testing against real data instead of a fixture.
    """
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            for s in _strings_in(v):
                yield s
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            for s in _strings_in(v):
                yield s


def published_dirs_of(job: dict) -> set:
    out = set()
    for s in _strings_in(job):
        out.update(_PUBLISH_DST.findall(s))
    return out


def read_queue_state(queue_dir: str, state: str):
    """[(stem, job-or-None)] for one queue subdir. Raises CannotCheck if absent."""
    d = os.path.join(queue_dir, state)
    if not os.path.isdir(d):
        raise CannotCheck("queue dir not readable: %s" % d)
    out = []
    stems = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(d, "*.json"))}
    for stem in sorted(stems):
        try:
            with open(os.path.join(d, stem + ".json"), "r", encoding="utf-8") as fh:
                out.append((stem, json.load(fh)))
        except Exception:
            out.append((stem, None))
    return out


def superseded_dirs(queue_dir: str) -> set:
    """Dirs some rc=0 job in done/ published into.

    THE DISCRIMINATOR THAT MAKES GATE 2 TRUE (2026-08-17). Without it the gate
    reports 15 entries and 9 are wrong: `ep2-b04-goblin-ipa-content`,
    `ep2-b06-ipa-guardcast-0812`, `ep2-b08-refresh` and all six
    `ep2-goblin-design-d*` have a LATER done/ entry with rc=0 publishing into the
    same directory, so the complete set on the branch is the successful run's
    output and the board is not wrong about the failed attempt.

    This is the same lesson as the rest of the day, encoded: before believing a
    `failed/` entry, read `done/` for the same directory. Two clips were nearly
    re-rendered and five jobs nearly re-fired for want of exactly this lookup.
    """
    out = set()
    for _, job in read_queue_state(queue_dir, "done"):
        if job is not None and job.get("rc") == 0:
            out.update(published_dirs_of(job))
    return out


def mislabelled_failures(queue_dir: str, ref=RESULTS_REF, main_ref="HEAD", repo=None):
    """GATE 2. [(stem, dir)] failed/ entries owning a complete set main cannot see."""
    complete = complete_sets(ref, repo)
    main_dirs = {job_dir_of(p) for p in farm_out_paths(main_ref, repo)} - {None}
    superseded = superseded_dirs(queue_dir)
    out, unreadable = [], []
    for stem, job in read_queue_state(queue_dir, "failed"):
        if job is None:
            unreadable.append(stem)
            continue
        for d in sorted(published_dirs_of(job)):
            if d in complete and d not in main_dirs and d not in superseded:
                out.append((stem, d))
    return out, unreadable


def report(results_ref=RESULTS_REF, main_ref="HEAD", repo=None, queue_dir=None,
           out=sys.stdout) -> int:
    rc = RC_OK

    # -- context: the raw divergence, which is expected to be large
    try:
        results = farm_out_paths(results_ref, repo)
        mainp = farm_out_paths(main_ref, repo)
    except CannotCheck as exc:
        out.write("!! CANNOT CHECK: %s\n" % exc)
        return RC_CANNOT_CHECK
    stranded = collections.Counter()
    for p in results - mainp:
        d = job_dir_of(p)
        if d:
            stranded[d] += 1
    out.write("divergence %s -> %s: %d path(s) in %d dir(s); %s holds %d dir(s)\n"
              % (results_ref, main_ref, sum(stranded.values()), len(stranded),
                 main_ref, len({job_dir_of(p) for p in mainp} - {None})))
    out.write("  (context, not a verdict: main holds a curated subset by policy -- "
              "see .gitignore on promoted frames. This number is never zero.)\n")

    # -- GATE 1
    try:
        bad = inconsistent_sets(results_ref, repo)
    except CannotCheck as exc:
        out.write("!! CANNOT CHECK set consistency: %s\n" % exc)
        return RC_CANNOT_CHECK
    out.write("gate 1, set consistency on %s: %d bad set(s)\n" % (results_ref, len(bad)))
    for d, why, f, l in bad:
        out.write("  BAD SET  %-38s %s (files=%d manifest_lines=%d)\n" % (d, why, f, l))
    if bad:
        rc = RC_STRANDED
        out.write("!! a manifest that disagrees with its own directory attested to "
                  "something nobody copied.\n")
    else:
        out.write("  ok  every published set's manifest matches its directory\n")
    try:
        unattested = unattested_sets(results_ref, repo)
    except CannotCheck as exc:
        out.write("!! CANNOT CHECK unattested sets: %s\n" % exc)
        return RC_CANNOT_CHECK
    out.write("  context: %d set(s) carry no manifest of either spelling%s\n"
              % (len(unattested),
                 " (" + ", ".join(unattested[:6])
                 + (" ..." if len(unattested) > 6 else "") + ")" if unattested else ""))

    # -- GATE 2
    if queue_dir is None:
        out.write("gate 2, mislabelled failures: SKIPPED (no --queue-dir; this half "
                  "did NOT run, and found nothing because it was not asked)\n")
        return rc
    try:
        mis, unreadable = mislabelled_failures(queue_dir, results_ref, main_ref, repo)
    except CannotCheck as exc:
        out.write("!! CANNOT CHECK mislabelled failures: %s\n" % exc)
        return RC_CANNOT_CHECK
    out.write("gate 2, failed/ entries owning a complete set absent from %s: %d\n"
              % (main_ref, len(mis)))
    for stem, d in mis:
        out.write("  MISLABELLED %-40s owns complete farm-out/%s\n" % (stem, d))
    for stem in unreadable:
        out.write("  UNREADABLE  %s -- cannot vouch for this entry\n" % stem)
    if mis or unreadable:
        rc = RC_STRANDED
        out.write("!! the board calls these failures and the results branch holds "
                  "complete attested sets for them. The board is wrong about what "
                  "is filmed.\n")
    else:
        out.write("  ok  no failed/ entry owns a complete set\n")
    return rc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="are the box's published results real, complete and visible to main?")
    ap.add_argument("--results-ref", default=RESULTS_REF)
    ap.add_argument("--main-ref", default="HEAD",
                    help="the ref every other question is asked of")
    ap.add_argument("--repo", default=None)
    ap.add_argument("--queue-dir", default=None,
                    help=r"queue root holding failed/, e.g. C:\banyan-queue")
    args = ap.parse_args(argv)
    return report(args.results_ref, args.main_ref, args.repo, args.queue_dir)


if __name__ == "__main__":
    sys.exit(main())
