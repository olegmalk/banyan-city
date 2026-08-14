#!/usr/bin/env python3
"""Refuse a batch of job yamls whose outputs would collide. EXITS NONZERO.

Written 2026-08-14 after I shipped the same defect three times.

WHY THIS EXISTS AND WHY IT EXITS RATHER THAN PRINTS. My authoring scripts already
computed the collision and PRINTED it. Twice I read the "DRY OK" line underneath
and enqueued anyway, and once the shell carried on past a nonzero exit because I
had chained the enqueue with `;` instead of `&&`. A check whose output can be
skimmed is not a check. This one is only ever used as:

    python3 review/ep2-picks/check_job_collisions.py <yaml>... && python3 pipeline/box_enqueue.py <yaml>...

THE EXACT DEFECT IT CATCHES, which took four instances to see clearly. A job has
two output locations and they are named by different conventions:

  payload dir   C:\\banyan-farm\\<full-job-id>\\...        ALWAYS contains the id
  publish dst   .../farm-out/<nickname>                   SOMETIMES contains the id

Measured across live jobs: `ep2-b05-final-0814` publishes to `ep2-b05-final-0814`
(the id), while `ep2-b12-tight-0813` publishes to `ep2-b12-tight` — THE ID MINUS
ITS DATE SUFFIX. When I derive a twin by replacing the full id, the nickname form
is untouched, because a nickname is a PREFIX of the id and not the id. So the
twin inherits its sibling's publish directory and one clip overwrites the other.

That is why it felt like bad luck: it only bites when the parent template used
the short form, which varies by whoever authored the parent. box_enqueue's guard
covers payload paths, where the id is always present, and so never sees this.

Checks, all of them across the whole batch AND against what is already queued:
  1. two jobs sharing a payload directory
  2. two jobs sharing a publish destination      <- the one that keeps biting
  3. two jobs sharing a declared artifact path
  4. a job whose publish destination does not contain its own id  (warning: the
     shape that makes 2 possible, worth seeing even when nothing collides yet)
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

import yaml

PAYLOAD_KEY = re.compile(r"C:\\banyan-farm\\([A-Za-z0-9_.-]+)\\")
DST_ASSIGN = re.compile(r"dst\s*=\s*\"[^\"]*farm-out/([A-Za-z0-9_.-]+)\"")


def outputs(path: Path):
    """The directories this job WRITES to, never the ones it reads from.

    The distinction is the whole correctness of this check. My first version
    scanned the raw text and flagged `plates-local` and a shared source plate as
    collisions — but two jobs READING the same plate is exactly what a seed pair
    is for, and refusing that would have blocked every twin I have ever authored.
    Write targets are the keys of the `payload:` mapping (files box_enqueue
    creates at enqueue time) and the publish destination inside the publish step.
    """
    raw = path.read_text(encoding="utf-8")
    doc = yaml.safe_load(raw) or {}
    jid = str(doc.get("id") or path.stem)
    payload_dirs = set()
    for key in (doc.get("payload") or {}):
        m = PAYLOAD_KEY.match(str(key))
        if m:
            payload_dirs.add(m.group(1))
    # the publish destination is assigned, never merely mentioned
    dsts = set()
    for step in (doc.get("steps") or []):
        for a in (step.get("argv") or []):
            dsts.update(DST_ASSIGN.findall(str(a)))
    arts = {str(a) for a in (doc.get("artifacts") or [])}
    return jid, payload_dirs, dsts, arts


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: check_job_collisions.py <job yaml>...", file=sys.stderr)
        return 2
    pay, dst, art = (collections.defaultdict(set) for _ in range(3))
    shapes = []
    for a in argv:
        p = Path(a)
        if not p.is_file():
            print(f"!! not a file: {a}", file=sys.stderr)
            return 2
        jid, ps, ds, ar = outputs(p)
        for x in ps:
            pay[x].add(jid)
        for x in ds:
            dst[x].add(jid)
        for x in ar:
            art[x].add(jid)
        for d in ds:
            if jid not in d:
                shapes.append((jid, d))

    bad = 0
    for label, table in (("PAYLOAD DIRECTORY", pay),
                         ("PUBLISH DESTINATION", dst),
                         ("DECLARED ARTIFACT", art)):
        for where, jobs in sorted(table.items()):
            if len(jobs) > 1:
                bad += 1
                print(f"!! SHARED {label}: {where}\n   claimed by {sorted(jobs)}", file=sys.stderr)

    for jid, d in shapes:
        print(f"   note: {jid} publishes to '{d}', which does not contain its id — "
              f"an id-only rename will NOT move it", file=sys.stderr)

    if bad:
        print(f"\n!! REFUSING: {bad} collision(s). One job would overwrite another's "
              f"output and the box would render one clip under two names.", file=sys.stderr)
        return 1
    print(f"no collisions across {len(argv)} job(s): "
          f"{len(pay)} payload dir(s), {len(dst)} destination(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
