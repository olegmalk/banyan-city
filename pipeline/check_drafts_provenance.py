#!/usr/bin/env python3
r"""Read `drafts_sha256` back out of rendered sidecars and say whether the
frames were drawn from the wording they were supposed to be drawn from.

WHY THIS EXISTS, 2026-08-17. Which wording a wave job renders is decided
entirely by which directory its `--harness` names: both samplers resolve their
prompts as `harness / "wave-drafts.yaml"` and NEVER from the `--root` checkout
they are handed. `box_enqueue.py` compares that harness copy against the repo's
when a job is FILED, and `goblin_ipa_sample.py --expect-drafts-sha256` now
compares it again when the job RUNS -- but the run-time flag is opt-in, the
harness copies get hand-synced while the queue is busy (`--sync-drafts` refuses
then), and every job filed before today carries neither check.

For all of those, the evidence is still on disk and always was: every sidecar
the samplers write records `drafts_sha256`, the hash of the exact prompts file
that produced that frame. Nothing has ever read it back. This reads it back.

It PREVENTS nothing -- it is the detector, not the guard -- and that is the
point: a mismatch nobody can prevent is still a mismatch somebody can catch
before the frame is scored, picked or published as canon. It is also how a job
that ran without `--expect-drafts-sha256` can be cleared after the fact, which
is what `pipeline/jobs/ep2-b08-cast-0817.yaml` currently asks its scorer to do
by hand.

Usage:
    # did this job's frames come from the wording the repo holds now?
    python3 pipeline/check_drafts_provenance.py farm-out/ep2-b08-cast-0817

    # against a specific wording rather than the repo's current one
    python3 pipeline/check_drafts_provenance.py --expect cbb3658e <paths...>

    # what wordings are in here at all? (reports, never fails)
    python3 pipeline/check_drafts_provenance.py --inventory farm-out

Exit codes, and they are the whole interface:
    0  every sidecar found carried drafts_sha256 and every one matched
    1  at least one sidecar was drawn from other wording  <-- the finding
    2  nothing checkable: no files, or no sidecar carried the field. NOT a pass.
       A thing that could not be checked was not checked.
    3  bad arguments

$0. Reads only; writes nothing, renders nothing, publishes nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

HEX = set("0123456789abcdef")
REPO = Path(__file__).resolve().parent.parent
REPO_DRAFTS = REPO / "pipeline" / "wave-drafts.yaml"

# Anchored at line start: `drafts_sha256:` appears inside prose in the job specs
# and in this file, and a substring search would pick those up as evidence.
FIELD = re.compile(r"^drafts_sha256:[ \t]*([0-9a-fA-F]+)[ \t]*$", re.MULTILINE)


def sidecar_drafts_sha(text: str):
    """The `drafts_sha256` a sidecar records, or None if it records none.

    None is NOT "matches" anywhere downstream: a sidecar without the field is
    a frame whose wording is unidentifiable, and that is reported as its own
    category rather than folded into the passes.
    """
    hits = FIELD.findall(text or "")
    if not hits:
        return None
    return hits[0].lower()


def matches(expect: str, actual: str) -> bool:
    """Prefix-tolerant hash comparison, >=8 hex digits.

    Same rule as goblin_ipa_sample.drafts_mismatch(): the specs and the prose
    quote short hashes (`cbb3658e`), so a prefix has to be usable, but anything
    shorter than 8 digits is too weak to distinguish two 350 KB files and is
    rejected by normalise_expect() before it ever reaches here.
    """
    want = (expect or "").strip().lower()
    have = (actual or "").strip().lower()
    if not want or not have:
        return False
    if len(want) == 64:
        return have == want
    return have.startswith(want)


def normalise_expect(raw: str):
    """(hash, None) for a usable expectation, else (None, why-not)."""
    want = (raw or "").strip().lower()
    if not want:
        return None, "no expected hash given"
    if len(want) < 8:
        return None, ("%r is only %d hex digits -- too short to tell two "
                      "350 KB wordings apart; give at least 8" % (raw, len(want)))
    if len(want) > 64 or any(c not in HEX for c in want):
        return None, "%r is not 8..64 hex digits of a sha256" % raw
    return want, None


def sidecars(paths) -> list:
    """Every *.yaml under the given files/dirs, sorted, deduplicated.

    `.png.meta.yaml` and the bare `.yaml` sidecars are both included; they are
    written as a pair and disagreeing halves would themselves be a finding.
    """
    found = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            found += sorted(path.rglob("*.yaml"))
        elif path.is_file():
            found.append(path)
    seen, out = set(), []
    for f in found:
        key = str(f.resolve())
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def audit(files, expect: str, read=None) -> dict:
    """Sort every sidecar into matched / diverged / fieldless / unreadable."""
    read = read or (lambda f: Path(f).read_text(encoding="utf-8",
                                                errors="replace"))
    res = {"matched": [], "diverged": [], "fieldless": [], "unreadable": []}
    for f in files:
        try:
            text = read(f)
        except OSError as exc:
            res["unreadable"].append((f, str(exc)))
            continue
        sha = sidecar_drafts_sha(text)
        if sha is None:
            res["fieldless"].append(f)
        elif matches(expect, sha):
            res["matched"].append((f, sha))
        else:
            res["diverged"].append((f, sha))
    return res


def verdict(res: dict) -> int:
    """The exit code, as a pure function of the audit, so it can be tested.

    Order matters and is deliberate: divergence is the finding and outranks
    everything, and an audit with nothing identifiable in it is rc 2 rather
    than the rc 0 an empty loop would otherwise hand back.
    """
    if res["diverged"]:
        return 1
    if not res["matched"]:
        return 2
    return 0


def group(pairs) -> dict:
    out = {}
    for f, sha in pairs:
        out.setdefault(sha, []).append(f)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="read drafts_sha256 back out of rendered sidecars")
    ap.add_argument("paths", nargs="+",
                    help="sidecar files, or directories walked for *.yaml")
    ap.add_argument("--expect", default=None, metavar="HEX",
                    help="the wording the frames should have come from; >=8 hex "
                         "digits. Default: sha256 of pipeline/wave-drafts.yaml "
                         "as this checkout holds it right now.")
    ap.add_argument("--inventory", action="store_true",
                    help="list every distinct wording found and exit 0 without "
                         "judging -- for asking what is in a tree, not whether "
                         "it is right")
    a = ap.parse_args(argv)

    files = sidecars(a.paths)
    if not files:
        print("!! no *.yaml under %s -- nothing to check, and nothing checked "
              "is not a pass." % ", ".join(a.paths))
        return 2

    if a.inventory:
        res = audit(files, "0" * 64)
        seen = group(res["matched"] + res["diverged"])
        print("== %d sidecar(s), %d distinct wording(s)" % (len(files), len(seen)))
        for sha, group_files in sorted(seen.items(), key=lambda kv: -len(kv[1])):
            print("  %s  x%-4d  e.g. %s"
                  % (sha[:12], len(group_files),
                     group_files[0].name if hasattr(group_files[0], "name")
                     else group_files[0]))
        if res["fieldless"]:
            print("  (no drafts_sha256 at all: %d file(s) -- these record no "
                  "wording and can never be cleared)" % len(res["fieldless"]))
        return 0

    raw = a.expect
    source = "--expect"
    if raw is None:
        if not REPO_DRAFTS.is_file():
            print("!! no %s to take a default expectation from; pass --expect"
                  % REPO_DRAFTS)
            return 3
        raw = hashlib.sha256(REPO_DRAFTS.read_bytes()).hexdigest()
        source = "pipeline/wave-drafts.yaml as this checkout holds it"
    expect, why = normalise_expect(raw)
    if why:
        print("!! %s" % why)
        return 3

    res = audit(files, expect)
    print("== drafts provenance, %d sidecar(s)" % len(files))
    print("   expecting %s  (%s)" % (expect, source))
    print("   matched   %d" % len(res["matched"]))
    for sha, group_files in sorted(group(res["diverged"]).items(),
                                   key=lambda kv: -len(kv[1])):
        print("\n!! DREW OTHER WORDING: %d frame(s) from drafts %s" %
              (len(group_files), sha))
        for f in group_files[:12]:
            print("     %s" % f)
        if len(group_files) > 12:
            print("     ... and %d more" % (len(group_files) - 12))
    if res["fieldless"]:
        print("\n   %d sidecar(s) carry no drafts_sha256 -- their wording is "
              "unidentifiable and they are not counted as matching:"
              % len(res["fieldless"]))
        for f in res["fieldless"][:6]:
            print("     %s" % f)
    for f, exc in res["unreadable"]:
        print("\n!! unreadable: %s (%s)" % (f, exc))

    rc = verdict(res)
    if rc == 1:
        print("\nDRAFTS-PROVENANCE: FAIL -- %d frame(s) were drawn from wording "
              "other than the one they are being judged against. They are not "
              "evidence about that wording, whatever they look like."
              % len(res["diverged"]))
    elif rc == 2:
        print("\nDRAFTS-PROVENANCE: UNKNOWN -- no sidecar here identified its "
              "wording. Not a pass.")
    else:
        print("\nDRAFTS-PROVENANCE: PASS matched=%d" % len(res["matched"]))
    return rc


if __name__ == "__main__":
    sys.exit(main())
