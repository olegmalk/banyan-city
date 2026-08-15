#!/usr/bin/env python3
"""box_enqueue's payload-collision guard, driven directly — no ssh, no box.

On 2026-08-13 two jobs derived from one parent, `ep2-b01-shape` and its twin,
declared the same five payload paths in one parent-named directory. Payloads are
written at ENQUEUE time, so the twin overwrote its sibling's prompt five seconds
later, before either job ran, and the card rendered the twin's clip under both
job names. Nothing in the queue could have caught it: `to_job` does not copy
`payload:` into the job json, so the box never learns which files a job was
handed. The guard is therefore local memory — an append-only index of paths this
machine has given out — and these cases are what it must and must not refuse.

The two halves of "live" are the thing to keep straight. A claim blocks because
its job is still queued on the box, OR because it is younger than the grace
window. The second half is not redundant: it is the only thing that sees a twin
enqueued during the seconds before its sibling reaches ready/, which is exactly
how the original overwrite happened.

Run: python3 pipeline/test_box_enqueue.py
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import box_enqueue as be  # noqa: E402

FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


# The five paths the real pair shared, kept as a fixture rather than read out of
# pipeline/jobs/: those specs get fixed (a2 already moved to its own directory),
# and a regression test that dies when the bug is fixed tests nothing.
SHARED = [
    r"C:\banyan-farm\ep2-b01-figgrow-055-r3\cover_crop.py",
    r"C:\banyan-farm\ep2-b01-figgrow-055-r3\b01-fig-prompt.txt",
    r"C:\banyan-farm\ep2-b01-figgrow-055-r3\b01-negative.txt",
    r"C:\banyan-farm\ep2-b01-figgrow-055-r3\b01-fig-jobs-encode.json",
    r"C:\banyan-farm\ep2-b01-figgrow-055-r3\b01-fig-jobs-render.json",
]
OWN_DIR = [p.replace("ep2-b01-figgrow-055-r3", "ep2-b01-shape-a2-0813") for p in SHARED]

NOW = 1_760_000_000.0


def claim(job, dests, ts=NOW, rid=None):
    return {"rid": rid or ("rid-" + job), "job": job, "ts": ts,
            "spec": "pipeline/jobs/%s.yaml" % job, "dests": dests}


def test_the_overwrite_that_happened_is_refused():
    sibling = claim("ep2-b01-shape-0813", SHARED, ts=NOW - 5)
    twin = claim("ep2-b01-shapeB-0813", SHARED, ts=NOW)
    problems = be.payload_collisions(twin, [sibling], live_ids=set(), now=NOW)
    check("the twin five seconds later is refused", len(problems) == 5)
    text = " ".join(problems)
    check("refusal names the job holding the path", "ep2-b01-shape-0813" in text)
    check("refusal names the colliding path", "b01-fig-prompt.txt" in text)
    check("refusal reads as a BLOCK like the gate refusals do",
          all(p.startswith("BLOCKED:") for p in problems))


def test_a_twin_with_its_own_directory_passes():
    sibling = claim("ep2-b01-shape-0813", SHARED)
    a2 = claim("ep2-b01-shape-a2-0813", OWN_DIR)
    check("distinct directories, same filenames -> allowed",
          be.payload_collisions(a2, [sibling], live_ids=set(), now=NOW) == [])


def test_only_the_shared_paths_are_named():
    # One file in common (a driver script), the rest separate: refuse that one,
    # and say which. A guard that dumps all five would hide which is the problem.
    mixed = claim("ep2-b01-other", [SHARED[0]] + OWN_DIR[1:])
    problems = be.payload_collisions(mixed, [claim("ep2-b01-shape-0813", SHARED, ts=NOW - 5)],
                                     live_ids=set(), now=NOW)
    check("one shared path -> exactly one problem", len(problems) == 1)
    check("and it is the shared one", "cover_crop.py" in problems[0])


def test_a_job_still_on_the_card_blocks_however_old_its_claim_is():
    # Liveness comes from the box here, not the clock: a render queued this
    # morning is still going to read its payload this afternoon.
    old = claim("ep2-b01-shape-0813", SHARED, ts=NOW - 86400)
    new = claim("ep2-b01-shapeB-0813", SHARED)
    check("claim older than grace but job still queued -> refused",
          len(be.payload_collisions(new, [old], {"ep2-b01-shape-0813"}, NOW)) == 5)


def test_a_finished_job_stops_owning_its_paths():
    old = claim("ep2-b01-shape-0813", SHARED, ts=NOW - 86400)
    new = claim("ep2-b01-shapeB-0813", SHARED)
    check("job gone from ready/ and running/, claim past grace -> allowed",
          be.payload_collisions(new, [old], live_ids=set(), now=NOW) == [])


def test_re_enqueueing_the_same_job_while_it_is_queued_is_refused():
    # DOCUMENTED CHOICE: the refusal is by path, not by id. A second copy of the
    # same spec overwrites the queued copy's inputs exactly as a twin would, so
    # sharing an id earns no exemption -- and once that copy leaves the queue the
    # paths are free again (the case above).
    first = claim("ep1-b03-plate-twin", SHARED, ts=NOW - 600)
    again = claim("ep1-b03-plate-twin", SHARED, rid="rid-second-run")
    check("same id, previous run still queued -> refused",
          len(be.payload_collisions(again, [first], {"ep1-b03-plate-twin"}, NOW)) == 5)
    check("same id, previous run finished -> allowed",
          be.payload_collisions(again, [first], set(), NOW) == [])


def test_a_claim_never_collides_with_itself():
    # The guard reads the index twice, and the second read contains the line it
    # just wrote. Matching on rid is what keeps that from refusing every job.
    mine = claim("ep2-b01-shape-0813", SHARED)
    check("our own reservation, re-read, is not a collision",
          be.payload_collisions(mine, [mine], {"ep2-b01-shape-0813"}, NOW) == [])
    check("the same id from a DIFFERENT run still collides",
          len(be.payload_collisions(mine, [claim("ep2-b01-shape-0813", SHARED,
                                                 rid="rid-other-run")],
                                    set(), NOW)) == 5)


def test_two_lanes_in_the_same_instant_leave_exactly_one_winner():
    # Neither job is on the card yet -- both are inside the grace window, which
    # is the whole point of that window. If both refused, both lanes would stall
    # and re-refuse on the retry, so the earlier (ts, job) proceeds.
    first = claim("aaa-job", SHARED, ts=NOW)
    second = claim("bbb-job", SHARED, ts=NOW + 0.001)
    check("the later writer yields",
          len(be.payload_collisions(second, [first, second], None, NOW)) == 5)
    check("the earlier writer proceeds",
          be.payload_collisions(first, [first, second], None, NOW) == [])


def test_a_dry_run_that_cannot_see_the_queue_still_sees_the_grace_window():
    fresh = claim("ep2-b01-shape-0813", SHARED, ts=NOW - 5)
    stale = claim("ep2-b01-shape-0813", SHARED, ts=NOW - 86400)
    twin = claim("ep2-b01-shapeB-0813", SHARED)
    check("live_ids unknown, sibling enqueued seconds ago -> refused",
          len(be.payload_collisions(twin, [fresh], None, NOW)) == 5)
    check("live_ids unknown, claim long past grace -> allowed",
          be.payload_collisions(twin, [stale], None, NOW) == [])


def test_a_job_with_no_payload_is_never_blocked():
    check("no payload paths -> nothing to collide",
          be.payload_collisions(claim("plain-job", []),
                                [claim("ep2-b01-shape-0813", SHARED)],
                                {"ep2-b01-shape-0813"}, NOW) == [])
    check("spec without a payload block -> no dests", be.payload_dests({"id": "x"}) == [])
    check("spec with a payload block -> its keys",
          be.payload_dests({"payload": {SHARED[0]: "body"}}) == [SHARED[0]])


def test_paths_are_compared_the_way_the_box_resolves_them():
    check("case-insensitive", be.norm_dest(r"C:\Banyan-Farm\X.TXT") == be.norm_dest(r"c:\banyan-farm\x.txt"))
    check("slash direction", be.norm_dest("C:/banyan-farm/x.txt") == be.norm_dest(r"C:\banyan-farm\x.txt"))
    check("doubled separators", be.norm_dest(r"C:\\banyan-farm\\x.txt") == be.norm_dest(r"C:\banyan-farm\x.txt"))
    check("surrounding whitespace", be.norm_dest("  C:\\banyan-farm\\x.txt  ") == be.norm_dest(r"C:\banyan-farm\x.txt"))
    # and the one that matters: a collision must not be missed over a capital.
    shouty = claim("shouty", [p.upper() for p in SHARED])
    check("a path differing only in case still collides",
          len(be.payload_collisions(shouty, [claim("ep2-b01-shape-0813", SHARED)],
                                    {"ep2-b01-shape-0813"}, NOW)) == 5)


def test_the_index_survives_a_damaged_line(tmp: str):
    path = os.path.join(tmp, "index.jsonl")
    be.reserve_payload(claim("job-one", SHARED[:1]), path)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("{not json at all\n\n")
    be.reserve_payload(claim("job-two", SHARED[1:2]), path)
    entries = be.read_payload_index(path)
    check("both good lines read back", [e["job"] for e in entries] == ["job-one", "job-two"])
    check("the unparseable line is skipped, not fatal", len(entries) == 2)
    check("dests survive the round trip", entries[0]["dests"] == SHARED[:1])
    check("a missing index is simply no claims",
          be.read_payload_index(os.path.join(tmp, "nope.jsonl")) == [])
    # One append per enqueue, so a peer lane appending at the same time cannot
    # clobber a claim the way a rewritten json would.
    check("each claim is exactly one line",
          sum(1 for line in open(path, encoding="utf-8") if line.strip()) == 3)


def test_an_unreachable_box_is_not_an_empty_queue():
    empty = "%s\n" % be.QUEUE_MARKER
    check("marker with no files -> a queue that is genuinely empty",
          be.parse_queue_listing(empty) == set())
    check("no marker -> None, meaning we could not look",
          be.parse_queue_listing("ssh: connect to host rtx5090 port 22: timed out") is None)
    check("no output at all -> None", be.parse_queue_listing("") is None)
    listing = "a-job-1755.json\nb-job-1756.json\n%s\n" % be.QUEUE_MARKER
    check("ids are filenames without .json",
          be.parse_queue_listing(listing) == {"a-job-1755", "b-job-1756"})
    check("non-json noise in the listing is ignored",
          be.parse_queue_listing("Volume in drive C\nx.json\n%s\n" % be.QUEUE_MARKER) == {"x"})


def test_the_guard_refuses_before_anything_is_written(tmp: str):
    # End to end through main(), with the box replaced: a refused spec must send
    # no payload, queue nothing, and exit nonzero. Refusing after the scp would
    # be no guard at all -- the overwrite happens during the scp.
    sent, queued = [], []
    orig = (be.send_payload, be.enqueue, be.queued_job_ids, be.PAYLOAD_INDEX,
            be.node_is_approved)
    be.send_payload = lambda payload: sent.append(payload)
    be.enqueue = lambda job, dest="ready": queued.append(job["id"])
    be.queued_job_ids = lambda: (set(), None)
    be.PAYLOAD_INDEX = os.path.join(tmp, "main-index.jsonl")
    be.node_is_approved = lambda node: (True, "test: approved_by founder")
    try:
        spec = {"id": "ep2-b01-shape", "node": "002b-first-citizen", "beat": 1,
                "consumer": "the test", "steps": [{"name": "s", "argv": ["x"]}],
                "payload": {p: "body" for p in SHARED}}
        a = os.path.join(tmp, "a.json")
        b = os.path.join(tmp, "b.json")
        with open(a, "w", encoding="utf-8") as fh:
            json.dump(spec, fh)
        with open(b, "w", encoding="utf-8") as fh:
            json.dump(dict(spec, id="ep2-b01-shapeB"), fh)

        rc = be.main([a])
        check("the first job is queued", rc == 0 and len(queued) == 1 and len(sent) == 1)
        rc = be.main([b])
        check("its twin exits nonzero", rc == 1)
        check("and nothing more was sent to the box", len(sent) == 1)
        check("and nothing more was queued", len(queued) == 1)

        # Both in ONE invocation: the second must see the first's claim.
        sent[:] = []
        queued[:] = []
        os.remove(be.PAYLOAD_INDEX)
        rc = be.main([a, b])
        check("two colliding specs in one run -> one queued, one refused",
              rc == 1 and len(queued) == 1 and len(sent) == 1)

        # A dry run touches nothing and needs no box at all.
        sent[:] = []
        queued[:] = []
        os.remove(be.PAYLOAD_INDEX)

        def unreachable():
            raise AssertionError("a dry run must not need the box")

        be.queued_job_ids = unreachable
        rc = be.main([a, "--dry-run"])
        check("--dry-run neither reads the box nor writes to it",
              rc == 0 and not sent and not queued)
        check("--dry-run leaves no reservation behind",
              not os.path.exists(be.PAYLOAD_INDEX))
        # ...but a pair dry-run TOGETHER must still see itself, because checking
        # a pair before sending it is the reason to dry-run a pair at all.
        check("--dry-run on both specs at once still reports the collision",
              be.main([a, b, "--dry-run"]) == 1)
    finally:
        (be.send_payload, be.enqueue, be.queued_job_ids, be.PAYLOAD_INDEX,
         be.node_is_approved) = orig


def main():
    print("box_enqueue payload-collision guard")
    test_the_overwrite_that_happened_is_refused()
    test_a_twin_with_its_own_directory_passes()
    test_only_the_shared_paths_are_named()
    test_a_job_still_on_the_card_blocks_however_old_its_claim_is()
    test_a_finished_job_stops_owning_its_paths()
    test_re_enqueueing_the_same_job_while_it_is_queued_is_refused()
    test_a_claim_never_collides_with_itself()
    test_two_lanes_in_the_same_instant_leave_exactly_one_winner()
    test_a_dry_run_that_cannot_see_the_queue_still_sees_the_grace_window()
    test_a_job_with_no_payload_is_never_blocked()
    test_paths_are_compared_the_way_the_box_resolves_them()
    test_an_unreachable_box_is_not_an_empty_queue()
    with tempfile.TemporaryDirectory() as td:
        test_the_index_survives_a_damaged_line(td)
    with tempfile.TemporaryDirectory() as td:
        test_the_guard_refuses_before_anything_is_written(td)
    print()
    if FAILURES:
        print("✗ %d failure(s): %s" % (len(FAILURES), ", ".join(FAILURES)))
        return 1
    print("✓ all box_enqueue collision cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
