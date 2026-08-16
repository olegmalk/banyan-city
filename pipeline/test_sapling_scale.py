#!/usr/bin/env python3
"""Tests for pipeline/check_sapling_scale.py. Pure logic, no GPU, no network.

    python3 pipeline/test_sapling_scale.py

Own file rather than lines in test_pipeline.py: that file is edited by several
lanes at once and this needs none of its fixtures.

The cases below are not invented. Every prompt string is copied from a real
draft or payload in this repo, because a classifier tested on prose written by
the same person who wrote the classifier proves nothing.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_sapling_scale import (  # noqa: E402
    FAIL, WARN, EXEMPT, OK, classify, read_draft_variants, read_job_payloads,
    fired_tasks, run,
)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok  {name}")
    else:
        print(f"  x   {name}\n        got  {got!r}\n        want {want!r}")
        FAILURES.append(name)


# -- classify -------------------------------------------------------------
# THE VIOLATION. Verbatim from pipeline/jobs/ep2-b15-leafB-0813.yaml:46.
check("`taller than he is` fails",
      classify("A SINGLE SMALL SAPLING STANDS BESIDE HIM — one slender stem with two "
               "big leaves, one plant and not a patch of them, taller than he is.")[0],
      FAIL)

# THE ANCHORS. Verbatim from wave-drafts b03:authored and b01:authored_ep3_sapling_reference.
check("`40cm` anchors the scale",
      classify("crouches low behind the pencil-thin trunk of a tiny 40cm sapling "
               "that hides almost none of him")[0],
      OK)
check("`knee high` anchors the scale",
      classify("A single slender sapling grows alone from bare earth, one thin curved "
               "stem, two big leaves, one bare side twig, knee high, whole plant in frame")[0],
      OK)
check("`no taller than the grass` anchors the scale",
      classify("A tiny sapling in green summer grass, exactly two oversized cotyledon "
               "leaves, the whole plant no taller than the grass around it")[0],
      OK)

# THE EXCLUSIONS, and these are the ones that matter. Getting either wrong turns
# the check into the cry-wolf pattern that got the runner watchdog disabled.
# `standing tall` is POSTURE (taste/steward-model.v1.md A7) -- beat 02 writes it
# NEXT TO `40cm`, so the anchor there is the number and not the adjective.
check("`standing tall` alone is NOT an anchor",
      classify("sprints in panic and dives behind a tiny mascot-simple sapling "
               "standing tall, dust kicking up from the grass")[0],
      WARN)
check("`standing tall` beside `40cm` is anchored by the NUMBER",
      classify("dives behind a tiny 40cm mascot-simple sapling standing tall")[0],
      OK)
check("`tiny` alone is NOT an anchor",
      classify("A tiny sapling in an open grassy field, whole plant in frame")[0],
      WARN)

# MACRO IS EXEMPT, not measured. This is the empirical finding of 2026-08-16:
# apparent height conflates shot scale with plant size, and beat 12's macro is
# correct framing rather than a continuity error.
check("held macro on a seedling is exempt",
      classify("A single small purple fig on the thinnest branch of a tiny sapling, "
               "the only fruit in frame. Held macro, extreme close-up")[0],
      EXEMPT)
check("a contradiction beats an exemption",
      classify("extreme close-up of a tiny sapling, taller than he is")[0],
      FAIL)

# NEGATIVES MUST NOT COUNT AS ASSERTIONS. A draft's `No ...` tail is concatenated
# onto its positive, and the corrected drafts ban the very terms this file looks
# for. If a ban registered as an anchor the check would silently invert.
check("`no taller than the grass` in a NEGATIVE tail still reads as the grass anchor",
      classify("A tiny sapling. No woman, no girl, no taller than the grass.")[0],
      OK)

# -- readers ---------------------------------------------------------------
DRAFTS = """\
# a provenance comment mentioning a sapling taller than he is — must be ignored
beats:
  '01':
    authored: >-
      A tiny 40cm sapling, whole plant in frame.
    # another comment about a sapling
    authored_b01_x: >-
      A tiny sapling with no scale stated at all.
  '18':
    authored: >-
      A fig on the thinnest branch of a tiny sapling. Held macro.
"""

v = read_draft_variants(DRAFTS)
check("reader finds every authored block", sorted(x[1] for x in v),
      ["authored", "authored", "authored_b01_x"])
check("reader keys blocks to their beat", sorted({x[0] for x in v}), [1, 18])
check("reader does not swallow comments into prompts",
      any("provenance comment" in x[2] for x in v), False)
check("reader joins wrapped lines", v[0][2], "A tiny 40cm sapling, whole plant in frame.")


def _tmp_repo():
    d = Path(tempfile.mkdtemp())
    (d / "pipeline" / "jobs").mkdir(parents=True)
    (d / "pipeline" / "measured").mkdir(parents=True)
    (d / "pipeline" / "wave-drafts.yaml").write_text(DRAFTS)
    (d / "pipeline" / "jobs" / "spec-ran.yaml").write_text(
        "payload:\n"
        "  C:\\x\\a-prompt.txt: 'A tiny sapling, taller than he is.'\n"
        "  C:\\x\\a-negative.txt: 'no taller than the grass, blurry'\n")
    (d / "pipeline" / "jobs" / "spec-unrun.yaml").write_text(
        "payload:\n"
        "  C:\\x\\b-prompt.txt: 'A tiny sapling, taller than he is.'\n")
    (d / "pipeline" / "measured" / "queue-history.json").write_text(
        '{"jobs": [{"task": "spec-ran", "spec_file": "pipeline/jobs/spec-ran.yaml"}],'
        ' "upcoming": []}')
    return d


d = _tmp_repo()

check("fired_tasks reads the ledger", "spec-ran" in fired_tasks(d), True)
check("a negative file is never read as a prompt",
      [p for _, pf, p in read_job_payloads(str(d)) if "negative" in pf], [])

# THE RECEIPT FILTER is the difference between a useful check and one that
# re-reports history forever -- the pattern that got the watchdog switched off.
f, gated = run(str(d))
check("run() gates on queue-history", gated, True)
check("a FIRED spec's violation is filtered out",
      any("spec-ran" in w for _, w, _ in f), False)
check("an UNRUN spec's violation still fails",
      [lv for lv, w, _ in f if "spec-unrun" in w], [FAIL])

f_all, _ = run(str(d), include_fired=True)
check("--all brings the fired receipt back",
      sorted(lv for lv, w, _ in f_all if "spec-" in w), [FAIL, FAIL])

# A missing ledger must NOT silently drop everything: absence of evidence that a
# job ran is not evidence that it did.
(d / "pipeline" / "measured" / "queue-history.json").unlink()
f_no, gated_no = run(str(d))
check("no ledger -> nothing is filtered, and the caller is told", gated_no, False)
check("no ledger -> both specs are still reported",
      len([w for _, w, _ in f_no if "spec-" in w]), 2)

print()
if FAILURES:
    print(f"x {len(FAILURES)} failure(s): " + "; ".join(FAILURES))
    sys.exit(1)
print("all sapling-scale tests pass")
sys.exit(0)
