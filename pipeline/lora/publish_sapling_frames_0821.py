#!/usr/bin/env python3
r"""Copy the box's finished inpaints onto main under their DATASET names.

WHY THIS IS A FILE AND NOT A COMMAND SOMEONE TYPES. The twenty-six v1 frames
got here by hand on 2026-08-21 -- `git show` per job, renamed one at a time --
and nothing recorded which courier directory each frame came out of. That is
fine exactly once. It stops being fine the moment there is a v2, because the
rename is where the dataset's provenance chain can silently break: the box
publishes `sap-<fid>-s20260820.png` (named for the SEED) and the manifest wants
`sap-<fid>-<plate>-0821.png` (named for the PLATE), so a fid/plate pair typed
wrong produces a frame that is captioned for a scene it is not standing in --
and every downstream check would pass it, because every downstream check reads
the manifest, which is generated from the same table that got it wrong.

WHAT IT REFUSES TO DO. Overwrite a frame that is already here. The frames on
main are the ones whose sha256s the committed manifest asserts and whose
captions are already written beside them; a re-run that quietly replaced one
would leave the manifest asserting a hash for a picture that is gone. --force
is the way to say you mean it.

WHERE THE BYTES COME FROM. `origin/farm-results-rtx5090`, the courier branch
the runner pushes itself -- never the local working tree, which does not have
them, and never a path on the box, which this machine cannot read. The branch
is fetched first, so a stale local ref cannot silently publish yesterday's run.

$0. git plumbing and a file copy. No model, no GPU, no network beyond the fetch.

  python3 pipeline/lora/publish_sapling_frames_0821.py            # dry
  python3 pipeline/lora/publish_sapling_frames_0821.py --write
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "pipeline"))
import build_sapling_lora_composites_0821 as B  # noqa: E402

BRANCH = "origin/farm-results-rtx5090"
FRAMES = "farm-out/ep3-saplora-frames-0821"
SEED = 20260820   # the box names its publish for the seed, not the plate


def git(*args, binary=False):
    p = subprocess.run(["git"] + list(args), cwd=REPO, capture_output=True)
    if p.returncode:
        return None
    return p.stdout if binary else p.stdout.decode("utf-8", "replace")


def main() -> int:
    write = "--write" in sys.argv
    force = "--force" in sys.argv

    if git("fetch", "origin", "farm-results-rtx5090", "-q") is None:
        print("!! could not fetch %s -- refusing to publish from a stale ref"
              % BRANCH)
        return 1
    listing = git("ls-tree", "-r", "--name-only", BRANCH, "farm-out/") or ""
    have = set(listing.splitlines())

    os.makedirs(os.path.join(REPO, FRAMES), exist_ok=True)
    pending, missing, kept = [], [], []
    for fid, pk, tier, root, height, tilt, lf, ls in B.ROWS:
        src = "farm-out/ep3-saplora-%s-0821/sap-%s-s%d.png" % (fid, fid, SEED)
        dst = "%s/sap-%s-%s-0821.png" % (FRAMES, fid, pk)
        if os.path.isfile(os.path.join(REPO, dst)) and not force:
            kept.append(fid)
            continue
        if src not in have:
            missing.append("%s (no %s on %s)" % (fid, src, BRANCH))
            continue
        pending.append((fid, pk, src, dst))

    for line in missing:
        print("   still on the card: %s" % line)
    print("%d already on main (kept), %d ready to publish, %d not yet drained"
          % (len(kept), len(pending), len(missing)))

    if not write:
        for fid, pk, src, dst in pending:
            print("  would publish %s -> %s" % (src, dst))
        print("-- dry run. re-run with --write.")
        return 0

    for fid, pk, src, dst in pending:
        blob = git("show", "%s:%s" % (BRANCH, src), binary=True)
        if not blob:
            print("!! %s: %s read empty off %s" % (fid, src, BRANCH))
            return 1
        with open(os.path.join(REPO, dst), "wb") as fh:
            fh.write(blob)
        print("  %s  %s  %d bytes  sha %s"
              % (fid, dst, len(blob), hashlib.sha256(blob).hexdigest()[:12]))
    print("published %d frame(s). Next: "
          "python3 pipeline/lora/build_sapling_0821.py --write" % len(pending))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
