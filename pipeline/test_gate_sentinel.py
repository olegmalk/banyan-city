#!/usr/bin/env python3
"""The sentinel's trigger, driven directly — no git, no ssh, no box.

The false positive is the whole risk. A watchdog that fires wrongly restarts a
healthy runner; a SENTINEL that fires wrongly renders something the founder has
not approved, which is the exact thing the gate exists to prevent. There is no
cheap failure on that side. So most of these cases are about NOT firing, and
the ones that do fire are the narrowest cases that can be described: a real
gate key, deleted, in a committed change that changed NOTHING ELSE, on a spec
with nothing else wrong.

"nothing else" is the third question here and it took a test to find it. The
first version of this file asked only "was the key deleted" and "is the spec
sound", and a commit that deleted `gate: founder` while moving --frames 121 to
217 answered yes to both. DIFF_CASES pins the missing rule down: the commit may
disturb comments and blank lines — it has to, the gate wears a DO NOT ENQUEUE
banner that goes with it — and may disturb nothing else.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gate_sentinel import (  # noqa: E402
    decide, diff_problems, gate_cleared, gate_key_present,
    commented_gate_present)

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

    ("a RIDER: the same commit that deleted the gate also retimed the render. "
     "This arrives as a problem like any other, and it is the reason the "
     "problems list is checked at all — an approval is for the recipe that was "
     "approved, not for whatever the commit also carried",
     obs(problems=["this commit ADDS a non-comment line, so it is not only a "
                   "gate clearing: - --frames 217"]), False),
]


def hunk(*lines):
    """A one-file unified diff. The header matters: everything before the first
    `@@` is git's own preamble, and a removed yaml line reading `-- foo` would
    look exactly like the `--- a/path` header to anything matching on prefix."""
    return "\n".join(
        ["diff --git a/pipeline/jobs/j.yaml b/pipeline/jobs/j.yaml",
         "index 1111111..2222222 100644",
         "--- a/pipeline/jobs/j.yaml",
         "+++ b/pipeline/jobs/j.yaml",
         "@@ -80,12 +80,4 @@ env:"] + list(lines)) + "\n"


# The shape of the CLEARING COMMIT, which is a separate question from "was the
# key deleted". It was deleted in every case below; the question is what else
# rode along. Each entry lists substrings the refusal must contain — an empty
# list means the commit is a clean clearing and fires. Naming the offending
# line is half the point: a refusal that says "something else changed" sends a
# human back to `git show`, and this tool exists to save exactly that trip.
DIFF_CASES = [
    ("the gate key alone, one line, nothing else in the commit",
     hunk(" id: ep1-b13",
          "-gate: founder",
          " consumer: the v35 assembly"), []),

    ("the real clearing this repo will make: the key, its `gate_ref:` block "
     "scalar, and the DO NOT ENQUEUE banner above them. The banner is comments "
     "and MUST be exempt — a human clearing a gate deletes the sign that says "
     "do not clear it, every single time, and a rule that refused this would "
     "refuse every clearing that will ever happen",
     hunk(" # STAGED, GATED.",
          "-#",
          "-# ============ DO NOT ENQUEUE. THE GATE BELOW IS CODE. ============",
          "-# `gate:`/`gate_ref:` make box_enqueue.py:123-132 refuse this file.",
          "-# WHAT MUST HAPPEN FIRST: Roman watches the 13s sample.",
          "-# =================================================================",
          "-gate: founder",
          "-gate_ref: >-",
          "-  ep1-b08-313f-vo-length-0811 must be screened and accepted first.",
          "-  Delete these two keys only after he has seen it.",
          "-",
          " consumer: the v35 assembly"), []),

    ("THE DANGEROUS ONE. Gate deleted and --frames moved 121 -> 217 in the same "
     "commit: a recipe the founder never approved, entering the queue under "
     "cover of an approval he did give. This is the 2026-07-25 failure with a "
     "commit as the vehicle",
     hunk("-gate: founder",
          " steps:",
          "-      - --frames 121",
          "+      - --frames 217"), ["--frames 217", "--frames 121"]),

    ("gate deleted and the seed changed. A reseed is a different render — the "
     "sample he approved was one draw and this is another",
     hunk("-gate: founder",
          " steps:",
          "-      - --seed 20260739",
          "+      - --seed 20260811"), ["--seed 20260811"]),

    ("gate deleted and a line ADDED. Nothing about an approval implies consent "
     "to a new argument, however harmless it looks",
     hunk("-gate: founder",
          " env:",
          "+  PYTORCH_CUDA_ALLOC_CONF: expandable_segments:True"),
     ["PYTORCH_CUDA_ALLOC_CONF"]),

    ("gate deleted and a line REMOVED elsewhere. Deleting a step is as much a "
     "recipe change as adding one — the plate step is what stops the 24.4% "
     "vertical stretch",
     hunk("-gate: founder",
          " steps:",
          "-  - name: plate"), ["- name: plate"]),

    ("gate deleted plus a whitespace-only change: the editor stripped trailing "
     "blanks on save. The line is the same line, so this fires",
     hunk("-gate: founder",
          "-consumer: the v35 assembly   ",
          "+consumer: the v35 assembly"), []),

    ("...but a RE-INDENT is not whitespace noise. Moving `gate:` under another "
     "key hides it from box_enqueue exactly as commenting it out would, and "
     "leading space is semantics in yaml",
     hunk("-gate: founder",
          " meta:",
          "+  gate: founder"), ["gate: founder"]),

    ("blank lines removed where the gate block used to be: formatting, not a "
     "recipe",
     hunk("-",
          "-gate: founder",
          "-"), []),

    ("a comment ADDED by the person clearing — `# cleared 2026-08-11, he said "
     "go` is the natural thing to write and must not block the fire",
     hunk("-gate: founder",
          "+# cleared 2026-08-11 — he watched the 313f sample and said go"), []),

    ("a removed yaml line that begins with two dashes. Read by prefix it is "
     "indistinguishable from git's own `--- a/path` header, which is why the "
     "reader waits for the first `@@` before believing anything",
     hunk("-gate: founder",
          "-- --frames 121"), ["--frames 121"]),

    ("a second hunk far from the gate, touching the prompt. Hunks are separate "
     "but the commit is one thing, and it is the commit that gets trusted",
     hunk("-gate: founder",
          " consumer: the v35 assembly",
          "@@ -300,3 +292,3 @@ steps:",
          "-        prompt: a thin green stem, still air",
          "+        prompt: a thin green stem, wind moving through it"),
     ["wind moving through it"]),

    ("an indented line removed AFTER the gate run was broken by a context "
     "line is not a `gate_ref:` continuation — the continuation only counts "
     "while it is still attached to the key it belongs to",
     hunk("-gate_ref: >-",
          "-  he must watch the 13s sample first",
          " steps:",
          "-  - name: render"), ["- name: render"]),

    ("an empty diff. Cannot happen from a real clearing, but the reader must "
     "not invent a problem out of nothing",
     "", []),
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
    for name, diff, wanted in DIFF_CASES:
        got = diff_problems(diff)
        joined = " | ".join(got)
        if bool(got) != bool(wanted):
            bad += 1
            print("FAIL  %s\n      expected %s got %s"
                  % (name, "a refusal" if wanted else "no problems",
                     joined or "no problems"))
        elif [s for s in wanted if s not in joined]:
            bad += 1
            print("FAIL  %s\n      refusal does not name %s: %s"
                  % (name, [s for s in wanted if s not in joined], joined))
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

    total = (len(DECIDE_CASES) + len(CLEARED_CASES) + len(COMMENT_CASES)
             + len(DIFF_CASES))
    print()
    if bad:
        print("✗ %d gate-sentinel case(s) failed" % bad)
        return 1
    print("✓ all %d gate-sentinel cases passed" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
