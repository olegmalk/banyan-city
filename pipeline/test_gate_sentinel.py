#!/usr/bin/env python3
"""The sentinel's trigger, driven directly — no git, no ssh, no box.

The false positive is the whole risk. A watchdog that fires wrongly restarts a
healthy runner; a SENTINEL that fires wrongly renders something the founder has
not approved, which is the exact thing the gate exists to prevent. There is no
cheap failure on that side. So most of these cases are about NOT firing, and
the two that do fire are the narrowest cases that can be described: a real gate
key, deleted, in a committed change, on a spec with nothing else wrong.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gate_sentinel import (  # noqa: E402
    decide, gate_cleared, gate_key_present, commented_gate_present)

SHA = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"


def obs(**kw):
    """A spec that just had its gate deleted and is otherwise clean. Each case
    below names only the field it is about, so the field under test is the only
    thing that can explain the verdict."""
    base = {"cleared_in": SHA, "gate_now": False, "commented_gate_now": False,
            "dirty": False, "already_fired": False, "problems": []}
    base.update(kw)
    return base


DECIDE_CASES = [
    # (name, obs, should_fire)
    ("the case this exists for: gate deleted in a commit, spec otherwise valid",
     obs(), True),

    ("gate STILL PRESENT — the b13 sample is unwatched and this is the whole "
     "point of the tool refusing",
     obs(gate_now=True), False),

    ("gate present AND a clearing recorded earlier: removed then put back, so "
     "HEAD is what counts and HEAD is gated",
     obs(gate_now=True, cleared_in=SHA), False),

    ("no clearing commit at all — the ordinary state of every spec in the "
     "directory, gated or not",
     obs(cleared_in=None), False),

    ("brand-new spec that never carried a gate: no parent version had the key, "
     "so nothing was cleared. This is the repo's real `-run.yaml` copy pattern "
     "and it must stay invisible to the trigger",
     obs(cleared_in=None), False),

    ("gate COMMENTED OUT rather than deleted. yaml never sees the key so "
     "box_enqueue would happily take it — nobody deleted anything, and this is "
     "the one shape where the downstream check cannot save us",
     obs(commented_gate_now=True), False),

    ("spec edited for an unrelated reason and left uncommitted: a lane is "
     "mid-edit and the committed fact is not the current one",
     obs(dirty=True), False),

    ("already enqueued once. Restarts lose nothing — the state file is on disk "
     "and MAX_ATTEMPTS keys on the id, so a second copy is a wasted slot",
     obs(already_fired=True), False),

    ("node not founder-approved (box_enqueue's own words). Enqueueing this "
     "SystemExits the daemon at farm_worker.py:517, it does not just fail",
     obs(problems=["node 002b-first-citizen is NOT founder-approved"]), False),

    ("unfilled recipe_slot — the value IS the recipe and inventing one is "
     "scaling an unapproved result",
     obs(problems=["BLOCKED: unfilled recipe_slot 'motion_recipe'"]), False),

    ("malformed yaml: the loud skip, never a guess at what was meant",
     obs(problems=["malformed yaml: ScannerError: mapping values not allowed"]), False),

    ("missing plate: the init the spec names is not in the repo",
     obs(problems=["plate missing: init review/x.png is not in the repo"]), False),

    ("no consumer named — standing rule, no work without one",
     obs(problems=["no consumer named -- standing rule is no work without one"]), False),

    ("an `after:` the sentinel cannot verify from here",
     obs(problems=["after: ep1-b08-313f-vo-length-0811 — this script cannot see"]), False),

    ("a still-gated spec is refused before anything else is even looked at, so "
     "a gated file with problems reports the gate, not the problems",
     obs(gate_now=True, problems=["malformed yaml: whatever"]), False),

    ("everything wrong at once still refuses",
     obs(gate_now=True, commented_gate_now=True, dirty=True,
         already_fired=True, problems=["node not approved"]), False),

    ("second real fire: a different clearing commit, nothing else changed — "
     "the rule depends on the fact, not on which commit carried it",
     obs(cleared_in="0f0e0d0c0b0a09080706050403020100ffeeddcc"), True),
]

# The two halves of the git fact, tested on text because that is what git hands
# back. `before` is "" when the file did not exist in the parent commit.
CLEARED_CASES = [
    ("gate deleted between the two versions",
     "id: x\ngate: founder\nnode: n\n", "id: x\nnode: n\n", True),

    ("gate still there — an unrelated edit to the same file",
     "id: x\ngate: founder\nsteps: []\n", "id: x\ngate: founder\nsteps: [a]\n", False),

    ("file did not exist in the parent: a new ungated spec is not a clearing",
     "", "id: x\nnode: n\nconsumer: y\n", False),

    ("gate ADDED, not removed — staging a job is the opposite of clearing it",
     "id: x\nnode: n\n", "id: x\ngate: founder\nnode: n\n", False),

    ("gate_ref alone counts: it blocks box_enqueue exactly as `gate:` does",
     "id: x\ngate_ref: >-\n  the 13s look\n", "id: x\n", True),

    ("gate emptied instead of deleted. `gate:` with no value is falsy, so "
     "box_enqueue would ALLOW it — the key was not deleted, so this is not a "
     "clearing and the sentinel stays out of it",
     "id: x\ngate: founder\n", "id: x\ngate:\n", False),

    ("the prose header every staged spec carries mentions the key inside a "
     "comment; removing prose is not removing a gate",
     "# `gate:`/`gate_ref:` make box_enqueue refuse\nid: x\ngate: founder\n",
     "# `gate:`/`gate_ref:` make box_enqueue refuse\nid: x\n", True),

    ("...and a file whose ONLY mention of a gate is that prose never counted "
     "as gated in the first place",
     "# `gate:`/`gate_ref:` make box_enqueue refuse\nid: x\n",
     "# a different comment\nid: x\n", False),

    ("an indented gate under some other mapping is not the top-level key "
     "box_enqueue reads, either before or after",
     "id: x\nmeta:\n  gate: founder\n", "id: x\nmeta: {}\n", False),
]

# The commented-gate reader on its own: this is the one shape box_enqueue
# cannot catch for us, so it is worth pinning down separately.
COMMENT_CASES = [
    ("a commented-out gate key", "id: x\n# gate: founder\n", True),
    ("no space after the hash", "id: x\n#gate: founder\n", True),
    ("indented commented gate", "id: x\n  # gate_ref: the 13s look\n", True),
    ("the standard prose header — a backtick sits where the key would start",
     "# `gate:`/`gate_ref:` make box_enqueue.py:123-132 refuse this file\n", False),
    ("prose that merely names the word gate",
     "# WHAT MUST HAPPEN FIRST: the gate on this clears when Roman looks\n", False),
    ("a bare `# gate:` with no value is prose, not a key",
     "# gate:\n", False),
    ("a live gate key is not a commented one", "gate: founder\n", False),
]


def main():
    bad = 0
    for name, o, want in DECIDE_CASES:
        got, why = decide(o)
        if got != want:
            bad += 1
            print("FAIL  %s\n      expected fire=%s got=%s (%s)" % (name, want, got, why))
        else:
            print("ok    %s" % name)

    print()
    for name, before, after, want in CLEARED_CASES:
        got = gate_cleared(before, after)
        if got != want:
            bad += 1
            print("FAIL  %s\n      expected cleared=%s got=%s" % (name, want, got))
        else:
            print("ok    %s" % name)

    print()
    for name, text, want in COMMENT_CASES:
        got = commented_gate_present(text)
        if got != want:
            bad += 1
            print("FAIL  %s\n      expected commented=%s got=%s" % (name, want, got))
        else:
            print("ok    %s" % name)

    print()
    # Every real staged spec in the repo must read as gated right now. This is
    # not a unit case — it is the live directory, and if one of them stops
    # reading as gated because someone reformatted a key, the trigger's own
    # premise has moved and the test should say so before the box does.
    jobs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs")
    gated = 0
    for name in sorted(os.listdir(jobs)):
        if not name.endswith(".yaml"):
            continue
        with open(os.path.join(jobs, name), encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        if gate_key_present(text):
            gated += 1
        elif commented_gate_present(text):
            bad += 1
            print("FAIL  %s reads as a COMMENTED gate — ambiguous, fix the file" % name)
    print("ok    %d staged specs in pipeline/jobs/ read as gated" % gated)
    if gated < 1:
        bad += 1
        print("FAIL  no spec in pipeline/jobs/ carries a gate — the reader is broken")

    total = len(DECIDE_CASES) + len(CLEARED_CASES) + len(COMMENT_CASES)
    print()
    if bad:
        print("✗ %d gate-sentinel case(s) failed" % bad)
        return 1
    print("✓ all %d gate-sentinel cases passed" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
