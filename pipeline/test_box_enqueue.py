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
    sent, queued, scanned = [], [], []
    orig = (be.send_payload, be.enqueue, be.queued_job_ids, be.PAYLOAD_INDEX,
            be.node_is_approved, be.prior_runs)
    be.send_payload = lambda payload: sent.append(payload)
    be.enqueue = lambda job, dest="ready": queued.append(job["id"])
    be.queued_job_ids = lambda: (set(), None)
    be.PAYLOAD_INDEX = os.path.join(tmp, "main-index.jsonl")
    be.node_is_approved = lambda node: (True, "test: approved_by founder")
    # The already-ran scan is a SECOND ssh on the enqueue path, and it has to be
    # stubbed here for the same reason as the first: this test runs in CI, where
    # the hostname does not resolve. It is a real box read, so leaving it live
    # would also mean every local test run doing `dir` on the card.
    be.prior_runs = lambda base, sha: (scanned.append(base)
                                       or ({"done": [], "failed": [], "sha": []},
                                           None))
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
        check("and done/ was consulted before it went", scanned == ["ep2-b01-shape"])
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

        def unreachable(*_args):
            raise AssertionError("a dry run must not need the box")

        be.queued_job_ids = unreachable
        be.prior_runs = unreachable
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
         be.node_is_approved, be.prior_runs) = orig


# --------------------------------------------------------------------------
# THE PLATE GUARD. Added 2026-08-16, after box_enqueue was found holding twelve
# i2v specs (eight on beat 06, two on 09, two on 10) off the card because one
# real scene reads as a card.
#
# These build the pictures rather than fetching them, and that is on purpose in
# both directions. Fetching would make the test a network test and it would pass
# vacuously wherever origin/farm-results-rtx5090 is not present -- a lane's first
# attempt at a different guard here tested "the file exists" and passed happily
# against a tree with the file deleted. Building them means the bytes go through
# cover_crop, border_flatness and plate_problems exactly as a real --src does, so
# what is exercised is the mechanism and not a proxy for it.
#
# The three grounds are the three cases the statistic has to tell apart, and the
# numbers they produce are the numbers measured on the real plates:
#
#   blank paper   flat in lightness AND in colour        -> refuse (and it does)
#   tinted ramp   flat in lightness, NOT flat in colour  -> refuse (and it does)
#   two materials flat in lightness, NOT flat in colour  -> refuse (AND IT IS
#                                                           WRONG, see below)
#
# The last two are why colour flatness was not swapped in as the decider: it
# cannot tell a card on a tinted ramp from a horizon, and swapping it released
# fourteen real costume sheets across the 2510-plate sweep.
PLATE_W, PLATE_H = 704, 1280


def _png(rows):
    """PNG bytes of a 704x1280 picture, `rows` giving the RGB of each row."""
    import io

    from PIL import Image
    im = Image.new("RGB", (PLATE_W, PLATE_H))
    px = im.load()
    for y in range(PLATE_H):
        c = rows(y)
        for x in range(PLATE_W):
            px[x, y] = c
    # a dark figure in the middle, clear of the 8% border band: every one of
    # these grounds has a character standing on it, and the guard must be
    # measuring the BORDER, not the subject.
    for y in range(300, 1100):
        for x in range(240, 470):
            px[x, y] = (60, 55, 70)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


BLANK_PAPER = _png(lambda y: (238, 235, 230))
# A costume card on a ground that cools from cream to pale blue down the frame,
# which is what most of the plates the colour rule released actually looked
# like. Only the blue channel moves, and blue carries 11% of luma, so 40 levels
# of tint is under 5 levels of lightness: flat to border_flatness, not flat to
# border_colour_flatness. The card is still a card.
TINTED_RAMP = _png(lambda y: (238, 235, 240 - (y * 40) // PLATE_H))
# sky over grass at the SAME lightness (both ~218 luma) and 43 levels apart in
# blue: the real plate's border, reduced to its two materials.
TWO_MATERIALS = _png(lambda y: (205, 222, 231) if y < PLATE_H * 0.55
                     else (216, 226, 188))


def _spec(src=r"c:\banyan-farm\courier-box\farm-out\ep2-x\plate.png", **kw):
    spec = {"id": "t", "steps": [{"name": "crop", "argv": ["p", "--src", src]},
                                 {"name": "render", "argv": ["ltx_i2v.py"]}]}
    spec.update(kw)
    return spec


def test_blank_paper_is_refused_and_says_so():
    problems = be.plate_problems(_spec(), fetch=lambda p: BLANK_PAPER)
    check("a figure on blank paper is refused", len(problems) == 1)
    check("and the refusal names it a CHARACTER CARD",
          "CHARACTER CARD" in problems[0])
    check("blank paper is flat in lightness",
          be.measure_plate(BLANK_PAPER) >= be.PLATE_FLAT_MAX)
    check("blank paper is flat in colour too",
          be.measure_plate_colour(BLANK_PAPER) >= be.PLATE_FLAT_MAX)


def test_a_card_on_a_tinted_ramp_stays_refused():
    # THE POSITIVE CONTROL FOR THE FIX THAT WAS NOT MADE. Colour flatness sees a
    # ramp as textured, so a rule that decided on colour would wave this card
    # straight through. It must keep failing.
    check("a tinted ramp is NOT flat in colour",
          be.measure_plate_colour(TINTED_RAMP) < be.PLATE_FLAT_MAX)
    check("and is refused anyway, because the decision is still on lightness",
          len(be.plate_problems(_spec(), fetch=lambda p: TINTED_RAMP)) == 1)


def test_the_two_material_border_is_the_KNOWN_FALSE_POSITIVE():
    # This pins a WRONG verdict on purpose. The real plate this reproduces --
    # farm-out/ep2-b10-patrol-scene-r2-0813/10-no-form-ipa-r0-w010-s1.png, a
    # field with a hedge, flowers and two guards -- was opened on 2026-08-16 and
    # is a scene, and the guard refuses it at 0.740. Nobody has found an
    # image-only rule that passes it and still refuses a costume turnaround.
    # WHOEVER FIXES THAT WILL BREAK THIS TEST. That is the intent: change it
    # deliberately, with a sweep behind you, not by nudging a threshold.
    flat = be.measure_plate(TWO_MATERIALS)
    colour = be.measure_plate_colour(TWO_MATERIALS)
    check("two materials at one lightness read as flat", flat >= be.PLATE_FLAT_MAX)
    check("but they are NOT one colour", colour < be.PLATE_FLAT_MAX)
    problems = be.plate_problems(_spec(), fetch=lambda p: TWO_MATERIALS)
    check("so a real scene is refused today", len(problems) == 1)
    check("and the refusal warns that this is what a horizon looks like",
          "LOOK BEFORE YOU BELIEVE THIS ONE" in problems[0])
    check("and prints the colour number it did not decide on",
          ("%.3f" % colour) in problems[0])


def test_the_two_card_refusals_are_reported_as_one_signal():
    plate = ["BLOCKED: ... looks like a CHARACTER CARD, ..."]
    refs = ["BLOCKED: ... from the COSTUME CARD reference set refs-x ..."]
    note = be.correlation_note(plate, refs)
    check("both card refusals -> the note fires", len(note) == 1)
    check("and it says one signal, not two", "ONE SIGNAL, NOT TWO" in note[0])
    check("flatness alone -> no note", be.correlation_note(plate, []) == [])
    check("refs alone -> no note", be.correlation_note([], refs) == [])
    # The unfetchable and unresolved refusals really are independent of the
    # border statistic -- "the bytes are not here" and "the spec is not here" --
    # and must not be labelled as sharing it.
    check("unfetchable + unresolved are NOT called one signal",
          be.correlation_note(["BLOCKED: could not fetch this job's --src"],
                              ["BLOCKED: could not work out which job produced"]) == [])


def test_a_stills_job_is_never_plate_checked():
    # A figure on blank paper is the CORRECT output of the identity lane. Only
    # i2v jobs are checked, or the shared queue closes on everybody else.
    stills = {"id": "t", "steps": [{"name": "crop", "argv": ["p", "--src", "x.png"]}]}
    check("no ltx_i2v in argv -> not checked",
          be.plate_problems(stills, fetch=lambda p: BLANK_PAPER) == [])


def test_a_picture_that_could_not_be_fetched_is_refused_not_waved_through():
    problems = be.plate_problems(_spec(), fetch=lambda p: None)
    check("unfetchable is a refusal", len(problems) == 1)
    check("and it says 'could not check' is not 'fine'",
          "could not fetch" in problems[0])
    check("a box-only --src has no results-branch path",
          be.results_branch_path(r"c:\banyan-farm\plates-local\x.png") is None)


# ---------------------------------------------------------------------------
# WHICH JOB DREW THIS PLATE. The refs guard has to name the producing spec
# before it can read its --refs, and until 2026-08-16 it looked for exactly one
# thing: pipeline/jobs/<farm-out dirname>.yaml. Nothing ever made those two
# names agree -- each spec's publish step is a hand-written literal, and the
# date suffix is usually dropped -- so 274 of the 645 directories on
# origin/farm-results-rtx5090 were refused with "no spec in pipeline/jobs for
# producing job X" while pipeline/jobs/X-0812.yaml sat right there. Beat 11's
# only staging-correct plate was one of them.
#
# THESE CASES RUN THE GUARD, NOT A PROXY FOR IT. Every one goes through
# be.refs_problems against spec files really written to a real directory, and
# the passing cases assert the producer's OWN reference set comes back in the
# refusal -- a thing that can only happen if the lookup actually opened it.
# Checking "the resolver returned a path" would have passed on a stub.
# ---------------------------------------------------------------------------

CARD_SET = "refs-guards-chosen-0814"      # a real member of CARD_REFS_DENYLIST


def _plate_json(out_dir, refs=CARD_SET):
    """A plate-generation spec: draws with `refs`, publishes into `out_dir`."""
    draw = ["python.exe", "goblin_ipa_beat.py", "--beat", "9",
            "--refs", "C:\\banyan-farm\\wave-goblin-prep\\" + refs]
    return {"steps": [
        {"name": "sample", "argv": draw},
        {"name": "publish", "argv": [
            "python.exe", "-c",
            'dst = "C:/banyan-farm/courier-box/farm-out/%s"\n'
            'os.makedirs(dst, exist_ok=True)\n' % out_dir]}]}


def _motion_on(dirname, plate="09-the-pause-s0.png", **kw):
    """A motion job conditioned on a picture published in farm-out/<dirname>."""
    src = "C:\\banyan-farm\\courier-box\\farm-out\\%s\\%s" % (dirname, plate)
    spec = {"id": "ep2-b09-motion-0816", "steps": [
        {"name": "crop", "argv": ["python.exe", "cover_crop.py", "--src", src]},
        {"name": "render", "argv": ["python.exe", "ltx_i2v.py", "--out", "clip.mp4"]}]}
    spec.update(kw)
    return spec


def _write_jobs(tmp, specs):
    for name, spec in specs.items():
        with open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
            json.dump(spec, fh)
    return tmp


def test_a_directory_named_for_its_spec_still_resolves(tmp):
    """The control. Whatever else changes, the old link must keep working."""
    _write_jobs(tmp, {"ep2-b09-guardpick-0814.json":
                      _plate_json("ep2-b09-guardpick-0814")})
    problems = be.refs_problems(_motion_on("ep2-b09-guardpick-0814"), jobs_dir=tmp)
    check("a directory named for its spec file resolves, as it always did",
          len(problems) == 1 and CARD_SET in problems[0])


def test_a_published_directory_that_dropped_the_date_suffix_resolves(tmp):
    """THE BUG, in the shape beat 11 has it.

    farm-out/ep2-b11-idfix was published by pipeline/jobs/ep2-b11-idfix-0812,
    which says so in its own publish step. Before the fix this refused with "no
    spec in pipeline/jobs for producing job 'ep2-b11-idfix'".
    """
    _write_jobs(tmp, {"ep2-b11-idfix-0812.json": _plate_json("ep2-b11-idfix")})
    problems = be.refs_problems(_motion_on("ep2-b11-idfix"), jobs_dir=tmp)
    check("a directory whose spec carries a date suffix resolves to that spec",
          len(problems) == 1 and "could not work out" not in problems[0])
    check("and the producer was really READ -- its own ref set comes back",
          len(problems) == 1 and CARD_SET in problems[0])


def test_two_specs_publishing_into_one_directory_REFUSE(tmp):
    """Ambiguity is a refusal, and it is not the same refusal as absence.

    Real, and the reason a `<dir>-DATE` name rule was not the fix:
    ep2-b15-seedC-0813 published into farm-out/ep2-b15-seedB. A name rule reads
    that plate's provenance off ep2-b15-seedB-0812 and is confidently wrong.
    """
    _write_jobs(tmp, {"ep2-b15-seedB-0812.json": _plate_json("ep2-b15-seedB",
                                                             refs="refs-clean"),
                      "ep2-b15-seedC-0813.json": _plate_json("ep2-b15-seedB")})
    problems = be.refs_problems(_motion_on("ep2-b15-seedB"), jobs_dir=tmp)
    check("a directory two specs publish into is REFUSED, not guessed at",
          len(problems) == 1 and "could not work out" in problems[0])
    check("and the refusal names both candidates, so a human can settle it",
          len(problems) == 1 and "ep2-b15-seedB-0812.json" in problems[0]
          and "ep2-b15-seedC-0813.json" in problems[0])
    check("it says two specs publish there rather than that none does",
          len(problems) == 1 and "2 specs publish into" in problems[0])


def test_a_directory_no_spec_claims_is_still_REFUSED(tmp):
    """The direction that must NOT loosen. A wider net is not the point."""
    _write_jobs(tmp, {"ep2-b09-guardpick-0814.json":
                      _plate_json("ep2-b09-guardpick-0814")})
    problems = be.refs_problems(_motion_on("b06-r6r7-recovered"), jobs_dir=tmp)
    check("a directory no spec in the repo claims is refused",
          len(problems) == 1 and "could not work out" in problems[0])
    check("and named, so the reader knows which directory is orphaned",
          len(problems) == 1 and "b06-r6r7-recovered" in problems[0])
    check("an empty jobs directory refuses too rather than crashing",
          len(be.refs_problems(_motion_on("anything"),
                               jobs_dir=os.path.join(tmp, "not-here"))) == 1)


def test_reading_a_directory_does_not_make_a_job_its_producer(tmp):
    """ep2-b01-lw-0815 reads farm-out/ep2-b01-final055-r3/... and publishes to
    its own directory. If a --src counted as a declaration, the plate's real
    producer would look ambiguous with the job asking about it."""
    reader = _motion_on("ep2-b01-final055-r3", plate="b01-final055-i55-s0.png")
    reader["steps"].append({"name": "publish", "argv": [
        "python.exe", "-c",
        'dst = "C:/banyan-farm/courier-box/farm-out/ep2-b01-lw-0815"']})
    _write_jobs(tmp, {"ep2-b01-final055-r3-0812.json":
                      _plate_json("ep2-b01-final055-r3"),
                      "ep2-b01-lw-0815.json": reader})
    problems = be.refs_problems(reader, jobs_dir=tmp)
    check("a --src is a picture being read, not a directory being claimed",
          len(problems) == 1 and CARD_SET in problems[0])


def test_the_real_beat_11_plate_resolves_in_the_real_pipeline_jobs():
    """Against the tree, not a fixture -- the house lesson from 2026-08-15.

    A guard test that builds its own world can pass while the real one is
    broken. farm-out/ep2-b11-idfix is a real published directory and
    pipeline/jobs/ep2-b11-idfix-0812.yaml is the real spec that wrote it.
    Nothing here files, unblocks or renders anything: it reads two files.
    """
    jobs = os.path.join(os.path.dirname(os.path.abspath(be.__file__)), "jobs")
    if not os.path.isdir(jobs):
        check("pipeline/jobs is present to check against", False)
        return
    problems = be.refs_problems(
        _motion_on("ep2-b11-idfix", plate="11-they-leave-wave1-s1.png"),
        jobs_dir=jobs)
    check("the real ep2-b11-idfix directory resolves to its real spec",
          not any("could not work out" in p for p in problems))
    check("the real ep2-b01-final055-r3 directory resolves too",
          not any("could not work out" in p for p in be.refs_problems(
              _motion_on("ep2-b01-final055-r3", plate="b01-final055-i55-s0.png"),
              jobs_dir=jobs)))
    check("and a directory nobody ever published still refuses",
          len(be.refs_problems(_motion_on("ep2-b11-idfix-that-never-ran"),
                               jobs_dir=jobs)) == 1)


def test_the_new_link_never_contradicts_the_old_one():
    """The property that makes this safe to trust: it only ADDS coverage.

    Over every spec in pipeline/jobs, no directory that has a spec file named
    for it is published into by a DIFFERENT spec -- so the resolver's first
    answer is never one the second would dispute. Measured 0 disagreements over
    all 645 published directories on 2026-08-16; this holds the repo half of it,
    which is the half that can change under us.
    """
    jobs = os.path.join(os.path.dirname(os.path.abspath(be.__file__)), "jobs")
    if not os.path.isdir(jobs):
        check("pipeline/jobs is present to check against", False)
        return
    claimed, disagree = {}, []
    for name in sorted(os.listdir(jobs)):
        if os.path.splitext(name)[1] not in (".yaml", ".yml", ".json"):
            continue
        try:
            spec = be.load_spec(os.path.join(jobs, name))
        except Exception:
            continue
        if not isinstance(spec, dict):
            continue
        for d in be.declared_out_dirs(spec):
            claimed.setdefault(d, []).append(name)
    for d, owners in claimed.items():
        named = be.producer_spec_path(d, jobs)
        if named and os.path.basename(named) not in owners:
            disagree.append((d, owners))
    check("no directory named for one spec is published into by another",
          not disagree)
    check("and the index is not empty, or the check above proves nothing",
          len(claimed) > 100)


# ---------------------------------------------------------------------------
# THE ALREADY-RAN GUARD.
#
# Twice the card has re-rendered a question it had already answered, because
# every collision guard above compares against LIVE work and a finished job owns
# nothing. 2026-08-19: ep2-b19-dropmotion-0819 filed twice sixteen minutes apart,
# 264s of GPU, two byte-identical mp4s. 2026-08-20: three jobs that finished at
# 04:56 sat unread until 12:20 and were re-filed clean by the resuming lane; b03
# re-rendered to completion.
#
# The cases below are the whole decision. A duplicate is refused, a REVISION is
# not -- diagnose/fix/re-render edits specs in place far more often than it
# renames them, and a guard that refuses the standing process gets switched off.
# No ssh: the directory listing and the finished records are injected.
# ---------------------------------------------------------------------------

B19 = "ep2-b19-dropmotion-0819"


def _ran_spec(**extra) -> dict:
    """The shape of the job that ran twice: a crop step and an ltx_i2v step."""
    spec = {
        "id": B19,
        "consumer": "the b19 motion lane",
        "steps": [
            {"name": "crop", "argv": ["python.exe", "cover_crop.py", "--src",
                                      "b19-init.png", "--size", "704x1280"]},
            {"name": "render", "argv": ["python.exe", "ltx_i2v.py", "--stage",
                                        "render", "--jobs", "jobs.json",
                                        "--frames", "121", "--crf", "10"]},
        ],
    }
    spec.update(extra)
    return spec


def _record(spec: dict, epoch: int = 1787128259, **extra) -> tuple:
    """(filename, the job record as the runner leaves it in done/).

    The runner writes back into the file it retires -- attempts, rc, started_at,
    finished_at, runner_pid, artifacts_present -- so a fixture without those
    would test a record shape that never exists on the box.
    """
    job = be.to_job(spec)
    job["id"] = "%s-%d" % (spec["id"], epoch)
    job = be.with_run_sha(job, spec.get("payload"))
    job.update({"attempts": 1, "rc": 0, "runner_pid": 4812,
                "runner_host": "rtx5090", "started_at": "2026-08-19T08:30:12Z",
                "finished_at": "2026-08-19T08:34:36Z",
                "artifacts_present": ["b19-drop.mp4"], "artifact_notes": []})
    job.update(extra)
    return job["id"] + ".json", job


def _listing(done=(), failed=(), sha=()) -> dict:
    return {"done": list(done), "failed": list(failed), "sha": list(sha)}


def _filed(spec: dict, again: bool = False) -> tuple:
    """(job, sha) as main() builds them, without touching the box."""
    job = be.with_run_sha(be.to_job(spec, again=again), spec.get("payload"))
    return job, job["spec_sha256"]


def test_a_clean_id_passes():
    """Nothing in done/, nothing in failed/, nothing queued: file it."""
    job, sha = _filed(_ran_spec())

    def never(_path):
        raise AssertionError("nothing matched, so no record should be read")

    check("an id the box has never seen is not refused",
          be.duplicate_problems(job, sha, _listing(), live_ids=set(),
                                read=never) == [])
    check("and a listing that matched OTHER beats is still clean",
          be.duplicate_problems(job, sha,
                                _listing(done=["ep2-b14-crf10-0819-1787000000.json",
                                               "ep2-b03-covermid-0820-1787200000.json"]),
                                live_ids={"ep2-b07-judge-0820-1787300000"},
                                read=never) == [])


def test_the_job_that_already_ran_is_refused_and_says_where_it_ran():
    """The 2026-08-19 re-file, driven directly. Same spec, same sha, done/."""
    spec = _ran_spec()
    name, record = _record(spec)
    job, sha = _filed(spec)
    problems = be.duplicate_problems(job, sha, _listing(done=[name]),
                                     live_ids=set(),
                                     spec_path="pipeline/jobs/%s.yaml" % B19,
                                     read=lambda p: record)
    check("the second filing of a finished job is refused", len(problems) == 1)
    said = problems[0] if problems else ""
    check("it reads as a BLOCK like every other refusal in the file",
          said.startswith("BLOCKED:"))
    check("names the id", B19 in said)
    check("names the directory it was found in", "in done/" in said)
    check("names the timestamped filename it found", name in said)
    check("names when it ran and how it exited",
          "2026-08-19T08:34:36Z" in said and "rc 0" in said)
    check("and names the exact invocation that overrides",
          "python3 pipeline/box_enqueue.py pipeline/jobs/%s.yaml --again" % B19
          in said)
    check("the refusal is loud about the cost rather than merely tidy",
          "264s" in said and "already" in said)


def test_a_job_that_failed_is_refused_too():
    """failed/ counts. A job that died on rc 92 does not become un-run.

    It is the weaker of the two directions on purpose -- re-running a failure
    can be exactly right -- so what this asserts is that the answer arrives as a
    refusal naming --again, not as silence.
    """
    spec = _ran_spec()
    name, record = _record(spec, epoch=1787129173, rc=92, failed_step="render",
                           finished_at="2026-08-19T09:02:11Z")
    job, sha = _filed(spec)
    problems = be.duplicate_problems(job, sha, _listing(failed=[name]),
                                     live_ids=set(), read=lambda p: record)
    check("a job sitting in failed/ is refused", len(problems) == 1)
    said = problems[0] if problems else ""
    check("and the refusal names failed/, not done/",
          "in failed/" in said and "in done/" not in said)
    check("carrying its rc so the reader can judge whether to re-run",
          "rc 92" in said)


def test_a_revision_is_not_a_duplicate():
    """Same id, DIFFERENT content: pass. This is the design call.

    Diagnose -> fix in the pipeline -> re-render is the standing process and it
    edits specs in place. If this refused, the guard would fire on most of what
    a lane legitimately does, and a guard that cries wolf gets switched off --
    this repo has already lost the runner watchdog for four days that way.
    """
    name, record = _record(_ran_spec())
    revised = _ran_spec()
    revised["steps"][1]["argv"][-1] = "14"          # crf 10 -> 14, a real change
    job, sha = _filed(revised)
    check("an edited spec files as a revision, not a duplicate",
          be.duplicate_problems(job, sha, _listing(done=[name]), live_ids=set(),
                                read=lambda p: record) == [])

    cosmetic = _ran_spec()
    cosmetic["steps"][1]["name"] = "render the drop"
    cosmetic["priority"] = 40
    cosmetic["task"] = "b19 drop motion, second look"
    job, sha = _filed(cosmetic)
    check("but renaming a step, renaming the task or renumbering the priority "
          "changes nothing the card renders, so it is still a duplicate",
          len(be.duplicate_problems(job, sha, _listing(done=[name]),
                                    live_ids=set(), read=lambda p: record)) == 1)


def test_the_sha_ignores_everything_the_runner_wrote_afterwards():
    """The record we compare against is one the runner has edited.

    execute() writes attempts, started_at, finished_at, rc, failed_step,
    runner_pid, runner_host, artifacts_present and artifact_notes back into the
    job file before retiring it. Hashing over a deny-list would read every
    finished job as a revision the first time the runner learned a new key.
    """
    spec = _ran_spec()
    _, record = _record(spec)
    job, _ = _filed(spec)
    check("a finished record hashes to what we filed",
          be.run_sha256(record) == be.run_sha256(job))
    check("and the enqueue-time stamp survives the round trip",
          record.get("spec_sha256") == job["spec_sha256"])

    stamped = be.inject_drafts_expectation(
        dict(job, steps=[dict(job["steps"][0]),
                         dict(job["steps"][1],
                              argv=job["steps"][1]["argv"] + ["--harness", "C:\\h"])]),
        spec, repo_sha="f" * 64)[0]
    check("the drafts hash this script injects is not part of the identity -- "
          "a --sync-drafts must not disguise a duplicate as a revision",
          be.run_sha256(stamped) == be.run_sha256(
              dict(job, steps=[dict(job["steps"][0]),
                               dict(job["steps"][1],
                                    argv=job["steps"][1]["argv"]
                                    + ["--harness", "C:\\h"])])))


def test_a_payload_only_edit_is_a_revision_where_the_record_can_show_it():
    """`payload:` is not copied into the job json, and that costs a comparison.

    Against a record filed since spec_sha256 exists, a changed prompt file is a
    revision and passes. Against an older record there is no payload to compare
    and the argv-only sha matches, so it refuses -- and the refusal has to SAY
    that, because "your prompt changed and I could not see it" is exactly the
    case where --again is the right answer rather than a shrug.
    """
    dest = r"C:\banyan-farm\b19\prompt.txt"
    first = _ran_spec(payload={dest: "the fruit drops past his shoulder"})
    name, record = _record(first)
    second = _ran_spec(payload={dest: "the fruit drops and rolls to a stop"})
    job, sha = _filed(second)
    check("two prompts, two shas", sha != record["spec_sha256"])
    check("so a prompt edit against a stamped record is a revision",
          be.duplicate_problems(job, sha, _listing(done=[name]), live_ids=set(),
                                read=lambda p: record) == [])

    old = dict(record)
    old.pop("spec_sha256")
    problems = be.duplicate_problems(job, sha, _listing(done=[name]),
                                     live_ids=set(), read=lambda p: old)
    check("against a record filed before the stamp existed it refuses",
          len(problems) == 1)
    check("and says plainly that the payload was NOT part of that comparison",
          "payload" in problems[0] and "--again" in problems[0])


def test_could_not_read_the_record_is_a_refusal_not_a_pass():
    """The law the rest of this file already keeps, one directory further on."""
    spec = _ran_spec()
    name, _ = _record(spec)
    job, sha = _filed(spec)
    problems = be.duplicate_problems(job, sha, _listing(done=[name]),
                                     live_ids=set(), read=lambda p: None)
    check("an unreadable prior record refuses", len(problems) == 1)
    check("and says what was not established, not that something is wrong",
          "NOT established" in problems[0] and "not 'fine'" in problems[0])

    check("an unreachable box is not an empty done/",
          be.parse_dup_listing("[done]\n[failed]\n[sha]\n") is None)
    check("but a box that answered with nothing found IS an empty done/",
          be.parse_dup_listing("[done]\n[failed]\n[sha]\n" + be.DUP_MARKER)
          == {"done": [], "failed": [], "sha": []})


def test_the_wildcard_listing_is_a_prefix_and_not_the_answer():
    """`dir /b <base>*.json` over-matches by design; the filter is here.

    ep2-b03-cover* also lists ep2-b03-covermid-0820, and refusing on that would
    be a confident wrong answer about a different beat.
    """
    job, sha = _filed(_ran_spec(id="ep2-b03-cover-0820"))

    def never(_path):
        raise AssertionError("a prefix match is not a match")

    check("a longer id sharing our prefix is not this job",
          be.duplicate_problems(job, sha,
                                _listing(done=["ep2-b03-covermid-0820-1787200000.json"]),
                                live_ids=set(), read=never) == [])
    check("base_job_id strips the epoch stamp",
          be.base_job_id("ep2-b19-dropmotion-0819-1787128259.json") == B19)
    check("and the --again token on top of it",
          be.base_job_id("ep2-b19-dropmotion-0819-1787128259-again0a1b2c.json") == B19)
    check("while a spec id that merely ends in a date keeps it",
          be.base_job_id("ep2-b15-listenroot-0820.json") == "ep2-b15-listenroot-0820")


def test_a_duplicate_under_a_nudged_name_is_caught_by_its_sha():
    """The id is how candidates are FOUND; the sha is what decides.

    A re-file under a nudged id has no id to match, so the sweep matches the
    stamped sha inside the records themselves. Zero-cost today (no record
    carries one yet) and self-activating as they turn over.
    """
    job, sha = _filed(_ran_spec(id="ep2-b19-dropmotion-b-0819"))
    hit = r"C:\banyan-queue\done\ep2-b19-dropmotion-0819-1787128259.json"

    def never(_path):
        raise AssertionError("a sha hit needs no record read")

    problems = be.duplicate_problems(job, sha, _listing(sha=[hit]), live_ids=set(),
                                     read=never)
    check("identical content under another name is refused", len(problems) == 1)
    check("and the refusal names the record it collided with",
          hit in problems[0] and "BYTE-IDENTICAL" in problems[0])

    same = _ran_spec()
    job, sha = _filed(same)
    name, record = _record(same)
    both = be.duplicate_problems(job, sha,
                                 _listing(done=[name],
                                          sha=[r"C:\banyan-queue\done\%s" % name]),
                                 live_ids=set(), read=lambda p: record)
    check("a record that matches on BOTH id and sha is one refusal, not two",
          len(both) == 1)


def test_a_job_already_queued_is_refused_whatever_its_sha():
    """The live half, and it answers differently from the finished half.

    A finished job's outputs exist and can be read; a twin filed into ready/
    races the original onto the same farm-out paths with nobody in between. Both
    incident write-ups assumed this door was already shut -- it was not: the
    live guard compares payload PATHS, so a spec with no `payload:` block was
    never compared to anything at all.
    """
    revised = _ran_spec()
    revised["steps"][1]["argv"][-1] = "14"
    job, sha = _filed(revised)

    def never(_path):
        raise AssertionError("a queued job has no finished record to read")

    problems = be.duplicate_problems(
        job, sha, _listing(), live_ids={B19 + "-1787128259"}, read=never)
    check("a revision filed while the original is still queued is refused",
          len(problems) == 1)
    check("and it says QUEUED rather than already ran",
          "ALREADY QUEUED" in problems[0] and "--list" in problems[0])
    check("live_ids=None -- the queue was not read -- drops only the live half",
          be.duplicate_problems(job, sha, _listing(), live_ids=None,
                                read=never) == [])


def test_again_overrides_and_mints_an_id_that_cannot_land_on_the_old_one():
    """--again is the escape hatch, and it must not destroy what it overrides.

    enqueue() moves with /Y, so an id identical to an existing record OVERWRITES
    it. A spec that opted out of stamping is exactly where that bites, which is
    why the token is minted below the epoch's resolution rather than from it.
    """
    spec = _ran_spec()
    name, record = _record(spec)
    job, sha = _filed(spec, again=True)
    problems = be.duplicate_problems(job, sha, _listing(done=[name]),
                                     live_ids=set(), read=lambda p: record)
    check("the refusal still fires -- --again overrides it, it does not skip it",
          len(problems) == 1)
    kept, notes = be.dup_override(problems, True, job["id"])
    check("--again clears the refusal", kept == [])
    check("and prints that it is overriding, with what it overrode",
          notes and "OVERRIDING" in notes[0]
          and any("already ran" in n.lower() for n in notes))
    check("without --again the same refusal stands",
          be.dup_override(problems, False, job["id"])[0] == problems)
    check("and --again with nothing refused says so rather than passing silently",
          be.dup_override([], True, job["id"])[1])

    check("the overriding id carries a token the plain one does not",
          "-again" in job["id"] and "-again" not in be.to_job(spec)["id"])
    check("it is still recognisably the same spec",
          be.base_job_id(job["id"]) == B19)
    minted = {be.to_job(spec, again=True)["id"] for _ in range(8)}
    check("and two overrides in the same second are two different filenames",
          len(minted) == 8)


def test_the_guard_actually_runs_on_the_enqueue_path():
    """A guard defined and never called is the hole it was written to close.

    main() cannot be driven without a box, so this pins the wiring: the scan is
    called, its unreadable answer exits rather than passing, --again reaches
    to_job, and the stamp goes onto the job before it is sent.
    """
    src = open(os.path.join(os.path.dirname(os.path.abspath(be.__file__)),
                            "box_enqueue.py"), encoding="utf-8").read()
    body = src[src.index("def main("):]
    check("main scans done/ and failed/ before filing", "prior_runs(" in body)
    check("main refuses to file when that scan could not run",
          "already-ran guard cannot run" in body)
    check("main stamps the sha onto the job it sends", "with_run_sha(" in body)
    check("main routes --again through to the id minting",
          "to_job(spec, again=args.again)" in body)
    check("and --again is a real flag with help text",
          '"--again"' in body and "mints a fresh id token" in body)
    check("the dry run says it did NOT consult done/",
          "cannot tell you whether this job already ran" in body)


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
    print("box_enqueue plate guard")
    test_blank_paper_is_refused_and_says_so()
    test_a_card_on_a_tinted_ramp_stays_refused()
    test_the_two_material_border_is_the_KNOWN_FALSE_POSITIVE()
    test_the_two_card_refusals_are_reported_as_one_signal()
    test_a_stills_job_is_never_plate_checked()
    test_a_picture_that_could_not_be_fetched_is_refused_not_waved_through()
    print()
    print("box_enqueue producer resolution")
    for case in (test_a_directory_named_for_its_spec_still_resolves,
                 test_a_published_directory_that_dropped_the_date_suffix_resolves,
                 test_two_specs_publishing_into_one_directory_REFUSE,
                 test_a_directory_no_spec_claims_is_still_REFUSED,
                 test_reading_a_directory_does_not_make_a_job_its_producer):
        with tempfile.TemporaryDirectory() as td:
            case(td)
    test_the_real_beat_11_plate_resolves_in_the_real_pipeline_jobs()
    test_the_new_link_never_contradicts_the_old_one()
    print()
    print("box_enqueue already-ran guard")
    test_a_clean_id_passes()
    test_the_job_that_already_ran_is_refused_and_says_where_it_ran()
    test_a_job_that_failed_is_refused_too()
    test_a_revision_is_not_a_duplicate()
    test_the_sha_ignores_everything_the_runner_wrote_afterwards()
    test_a_payload_only_edit_is_a_revision_where_the_record_can_show_it()
    test_could_not_read_the_record_is_a_refusal_not_a_pass()
    test_the_wildcard_listing_is_a_prefix_and_not_the_answer()
    test_a_duplicate_under_a_nudged_name_is_caught_by_its_sha()
    test_a_job_already_queued_is_refused_whatever_its_sha()
    test_again_overrides_and_mints_an_id_that_cannot_land_on_the_old_one()
    test_the_guard_actually_runs_on_the_enqueue_path()
    print()
    if FAILURES:
        print("✗ %d failure(s): %s" % (len(FAILURES), ", ".join(FAILURES)))
        return 1
    print("✓ all box_enqueue collision and plate-guard cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
