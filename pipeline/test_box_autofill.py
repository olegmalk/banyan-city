#!/usr/bin/env python3
"""box_autofill's depth rule and backlog rule, driven directly — no ssh, no box.

Every case here is a way the card has actually gone dark, or a way an autofill
could make things worse than a dark card:

  * `.HOLD` counted as depth. Six parked files sat in `ready/` on the night this
    was written and `dir /b ready` counts every one of them. A depth check that
    trusts a listing declares a queue of six holds healthy and lets the card
    idle for hours.
  * job count instead of minutes. Four publish steps is four minutes of work and
    four LTX takes is twenty-three; one number cannot stand for both.
  * an empty backlog rounding to "fine". The whole design is that an empty
    backlog is a LOUD state and never a licence to invent filler.
  * a stale or already-run entry firing. A backlog entry names an init that was
    true when it was filed; firing it eleven hours later animates a plate a lane
    has since replaced.
  * a guard refusal getting swallowed on the way to the backlog. Work reaching
    ready/ at 4am with nobody watching must have had MORE checking, not less.

Run: python3 pipeline/test_box_autofill.py
"""

import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import box_autofill as af  # noqa: E402
import box_enqueue as be  # noqa: E402

FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


def job(jid, kind="ltx", priority=100, filed_at="now", expires_h=None):
    """A job file as box_enqueue --backlog would have written it.

    `filed_at="now"` is the default because that is what a filed entry always
    carries; pass None to build the pathological entry with no clock at all.
    """
    script = {"ltx": "ltx_i2v.py", "still": "render_wave_sample.py",
              "charref": "goblin_ipa_beat.py", "inpaint": "inpaint_fruit.py",
              "other": "publish.py"}[kind]
    j = {"id": jid, "priority": priority, "needs_gpu": True,
         "steps": [{"argv": ["python", script, "--src", "x.png"]}],
         "artifacts": []}
    if filed_at is not None:
        j["backlog"] = {"filed_at": time.time() if filed_at == "now" else filed_at,
                        "expires_h": af.DEFAULT_EXPIRES_H if expires_h is None
                        else expires_h}
    return j


def write(root, sub, name, body):
    d = os.path.join(root, sub)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name)
    with open(path, "w", encoding="utf-8") as fh:
        if isinstance(body, dict):
            json.dump(body, fh)
        else:
            fh.write(body)
    return path


# --------------------------------------------------------------------------
# depth
# --------------------------------------------------------------------------

def test_hold_files_are_not_depth(root):
    write(root, "ready", "a.json", job("a"))
    # the exact spellings found in ready/ on 2026-08-15
    write(root, "ready", "b.json.HOLD", job("b"))
    write(root, "ready", "c.json.HOLD-wrong-action", job("c"))
    write(root, "ready", "d.json.HOLD-wrong-init", job("d"))
    minutes, count, kinds = af.queue_minutes(root, "ready")
    check("a .HOLD job is not counted as depth", count == 1)
    check("depth is the one runnable job's minutes", minutes == af.KIND_MINUTES["ltx"])
    check("kinds report only the runnable job", kinds == {"ltx": 1})


def test_depth_is_minutes_not_jobs(root):
    for i in range(4):
        write(root, "ready", "s%d.json" % i, job("s%d" % i, kind="still"))
    minutes, count, _ = af.queue_minutes(root, "ready")
    check("four stills are four jobs", count == 4)
    check("four stills are under four minutes of work", minutes < 4.0)
    plan = af.plan_fill([], set(), minutes, count, time.time())
    check("a job count of four does NOT read as a full queue",
          plan["status"] == "backlog_empty")


def test_running_is_not_counted_as_ready_depth(root):
    write(root, "running", "live.json", job("live"))
    minutes, count, _ = af.queue_minutes(root, "ready")
    check("a claimed job is not unclaimed depth", (minutes, count) == (0.0, 0))


def test_an_unreadable_ready_file_is_not_worth_zero(root):
    write(root, "ready", "broken.json", "{not json")
    minutes, count, kinds = af.queue_minutes(root, "ready")
    check("an unreadable queued file still counts as work",
          count == 1 and minutes == af.KIND_FALLBACK and kinds == {"unreadable": 1})


# --------------------------------------------------------------------------
# the fill rule
# --------------------------------------------------------------------------

def test_a_full_queue_is_left_alone():
    entries = [("x.json", job("x"))]
    plan = af.plan_fill(entries, set(), 60.0, 10, time.time())
    check("a queue over the floor files nothing",
          plan["status"] == "full" and plan["file"] == [])


def test_it_fills_only_up_to_the_floor():
    entries = [("j%d.json" % i, job("j%d" % i)) for i in range(20)]
    plan = af.plan_fill(entries, set(), 0.0, 0, time.time(),
                        floor=11.0, max_files=99)
    check("it stops as soon as the floor is met", len(plan["file"]) == 2)
    check("it does not empty the backlog into ready/", plan["minutes_after"] >= 11.0)


def test_the_per_tick_cap_holds():
    entries = [("j%d.json" % i, job("j%d" % i)) for i in range(20)]
    plan = af.plan_fill(entries, set(), 0.0, 0, time.time(), floor=999.0)
    check("no more than MAX_FILES_PER_TICK in one tick",
          len(plan["file"]) == af.MAX_FILES_PER_TICK)


def test_priority_order_is_the_runners_order(root):
    write(root, "backlog", "zz.json", job("zz", priority=10))
    write(root, "backlog", "aa.json", job("aa", priority=90))
    entries = af.backlog_entries(root)
    check("the backlog is read in (priority, name) order, as ready/ is",
          [n for n, _ in entries] == ["zz.json", "aa.json"])
    plan = af.plan_fill(entries, set(), 0.0, 0, time.time(), floor=1.0)
    check("priority 10 goes before an alphabetically earlier priority 90",
          plan["file"] == ["zz.json"])


def test_an_entry_with_no_clock_at_all_is_refused(root):
    """No stamp and no file to age: unverifiable freshness is not freshness."""
    plan = af.plan_fill([("nostamp.json", job("nostamp", filed_at=None))],
                        set(), 0.0, 0, time.time())
    check("an entry whose age cannot be established does not fire",
          plan["file"] == [] and plan["expired"] == ["nostamp.json"])


# --------------------------------------------------------------------------
# the loud empty state
# --------------------------------------------------------------------------

def test_an_empty_backlog_is_a_loud_state_not_an_invention():
    plan = af.plan_fill([], set(), 0.0, 0, time.time())
    check("a hungry card with no backlog reports backlog_empty",
          plan["status"] == "backlog_empty")
    check("it says nothing was invented", "NOTHING WAS INVENTED" in plan["why"])
    check("it files nothing at all", plan["file"] == [])


def test_backlog_exhaustion_mid_fill():
    entries = [("only.json", job("only"))]
    plan = af.plan_fill(entries, set(), 0.0, 0, time.time(), floor=999.0)
    check("it files everything eligible", plan["file"] == ["only.json"])
    check("running out mid-fill is still a fill, not a failure",
          plan["status"] == "filled")
    later = af.plan_fill([], set(), plan["minutes_after"], 1, time.time(), floor=999.0)
    check("the NEXT tick with nothing left is the loud one",
          later["status"] == "backlog_empty")


def test_the_tick_exits_2_when_it_is_hungry_with_nothing_to_draw(root):
    rc = af.main(["--root", root])
    check("a hungry tick with an empty backlog exits 2", rc == 2)
    with open(os.path.join(root, af.STATE_NAME), encoding="utf-8") as fh:
        st = json.load(fh)
    check("the state file records the hungry state", st["status"] == "backlog_empty")
    with open(os.path.join(root, af.LOG_NAME), encoding="utf-8") as fh:
        check("the log says BACKLOG EMPTY out loud", "BACKLOG EMPTY" in fh.read())


# --------------------------------------------------------------------------
# staleness: the two refusals of its own
# --------------------------------------------------------------------------

def test_a_superseded_entry_is_never_refiled():
    entries = [("done-already.json", job("done-already"))]
    plan = af.plan_fill(entries, {"done-already"}, 0.0, 0, time.time())
    check("a job id already run is not filed again", plan["file"] == [])
    check("and it is named as superseded", plan["superseded"] == ["done-already.json"])
    check("a superseded-only backlog is the loud empty state, not a fill",
          plan["status"] == "backlog_empty")


def test_an_expired_entry_is_not_fired():
    now = time.time()
    old = job("stale", filed_at=now - 40 * 3600, expires_h=36)
    fresh = job("fresh", filed_at=now - 60, expires_h=36)
    plan = af.plan_fill([("stale.json", old), ("fresh.json", fresh)],
                        set(), 0.0, 0, now, floor=1.0)
    check("a 40-hour-old entry with a 36h life does not fire",
          plan["expired"] == ["stale.json"])
    check("the fresh one still does", plan["file"] == ["fresh.json"])


def test_an_unstamped_entry_expires_off_its_mtime(root):
    d = os.path.join(root, "backlog")
    os.makedirs(d, exist_ok=True)
    p = write(root, "backlog", "handplaced.json", job("handplaced", filed_at=None))
    old = time.time() - 100 * 3600
    os.utime(p, (old, old))
    entries = af.backlog_entries(root)
    check("a hand-placed file with no stamp is still expired by its mtime",
          af.is_expired(entries[0][1], time.time(), p))


def test_a_refused_entry_keeps_its_bytes_and_says_why(root):
    now = time.time()
    write(root, "backlog", "stale.json", job("stale", filed_at=now - 99 * 3600))
    write(root, "backlog", "ran.json", job("ran", filed_at=now))
    write(root, "done", "ran.json", job("ran"))
    st = af.tick(root, now=now)
    names = os.listdir(os.path.join(root, "backlog"))
    check("the expired entry is parked, not deleted", "stale.json.EXPIRED" in names)
    check("the superseded entry is parked, not deleted", "ran.json.SUPERSEDED" in names)
    check("neither reached ready/", af.json_names(os.path.join(root, "ready")) == [])
    check("a backlog of only refused entries reports empty",
          st["status"] == "backlog_empty")


# --------------------------------------------------------------------------
# it actually moves files, and never the wrong ones
# --------------------------------------------------------------------------

def test_a_real_tick_files_from_backlog_into_ready(root):
    write(root, "backlog", "one.json", job("one", filed_at=time.time()))
    write(root, "backlog", "two.json.HOLD", job("two", filed_at=time.time()))
    st = af.tick(root)
    ready = af.json_names(os.path.join(root, "ready"))
    back = os.listdir(os.path.join(root, "backlog"))
    check("the eligible job is now in ready/", ready == ["one.json"])
    check("it was MOVED, not copied", "one.json" not in back)
    check("a .HOLD in the backlog is left exactly where it was",
          back == ["two.json.HOLD"])
    check("the state file names what it filed", st["filed"] == ["one.json"])


def test_a_dry_run_moves_nothing(root):
    write(root, "backlog", "one.json", job("one", filed_at=time.time()))
    st = af.tick(root, dry_run=True)
    check("a dry run says what it would file", st["filed"] == ["one.json"])
    check("and files nothing", af.json_names(os.path.join(root, "ready")) == [])
    check("and writes no state file",
          not os.path.exists(os.path.join(root, af.STATE_NAME)))


def test_it_never_unholds_a_parked_job(root):
    write(root, "ready", "held.json.HOLD-wrong-init", job("held"))
    write(root, "backlog", "parked.json.EXPIRED", job("parked"))
    af.tick(root)
    check("a .HOLD in ready/ is still a .HOLD",
          os.listdir(os.path.join(root, "ready")) == ["held.json.HOLD-wrong-init"])
    check("an .EXPIRED entry is never resurrected",
          os.listdir(os.path.join(root, "backlog")) == ["parked.json.EXPIRED"])


def test_it_never_touches_a_running_job(root):
    live = write(root, "running", "live.json", job("live"))
    before = os.stat(live).st_mtime
    write(root, "backlog", "one.json", job("one", filed_at=time.time()))
    af.tick(root)
    check("the claimed job is where the runner left it", os.path.exists(live))
    check("and was not rewritten", os.stat(live).st_mtime == before)


def test_a_job_id_in_ready_is_not_filed_twice(root):
    write(root, "ready", "dup.json", job("dup"))
    write(root, "backlog", "dup.json", job("dup", filed_at=time.time()))
    af.tick(root)
    check("the queued copy stands alone",
          af.json_names(os.path.join(root, "ready")) == ["dup.json"])
    check("the backlog copy is parked as superseded",
          os.listdir(os.path.join(root, "backlog")) == ["dup.json.SUPERSEDED"])


# --------------------------------------------------------------------------
# the guards on the way IN
# --------------------------------------------------------------------------

def test_a_fill_that_moved_nothing_does_not_report_filled(root):
    """A green tick over a queue that did not grow is this project's signature bug."""
    write(root, "backlog", "one.json", job("one"))
    real_rename = os.rename
    try:
        os.rename = lambda *a, **k: (_ for _ in ()).throw(OSError("locked"))
        st = af.tick(root)
    finally:
        os.rename = real_rename
    check("a fill where every move failed is not 'filled'", st["status"] == "blocked")
    check("and it names how many it wanted", "1 job(s)" in st["why"])
    check("and nothing is claimed to have been filed", st["filed"] == [])


def test_a_wedged_drainer_is_not_reported_as_a_healthy_queue(root):
    """A full queue and a dead card look identical unless this is asked."""
    now = time.time()
    write(root, "ready", "waiting.json", job("waiting"))
    write(root, "", "runner.log", "quiet")
    log = os.path.join(root, "runner.log")
    os.utime(log, (now - 20 * 60, now - 20 * 60))
    st = af.drainer_state(root, now)
    check("work waiting, nothing claimed, runner silent 20m reads as stalled",
          st["stalled"] and "NOBODY IS DRAINING" in st["why"])
    rc = af.main(["--root", root])
    check("and the tick exits 3, not 0", rc == 3)


def test_a_stall_is_not_declared_over_a_live_or_quiet_card(root):
    now = time.time()
    write(root, "", "runner.log", "x")
    check("an empty queue is not a stall -- silence is correct there",
          not af.drainer_state(root, now)["stalled"])
    write(root, "ready", "waiting.json", job("waiting"))
    write(root, "running", "live.json", job("live"))
    check("a claimed job is never a stall",
          not af.drainer_state(root, now)["stalled"])
    os.remove(os.path.join(root, "running", "live.json"))
    check("a runner that wrote a moment ago is not a stall",
          not af.drainer_state(root, now)["stalled"])
    os.remove(os.path.join(root, "runner.log"))
    check("an unreadable log is a broken probe, not evidence of a wedge",
          not af.drainer_state(root, now)["stalled"])


def test_filing_work_does_not_look_like_a_stall(root):
    """The runner polls every 10s; a job filed this second has not been offered."""
    now = time.time()
    write(root, "", "runner.log", "x")
    os.utime(os.path.join(root, "runner.log"), (now - 60 * 60, now - 60 * 60))
    write(root, "backlog", "one.json", job("one"))
    st = af.tick(root, now=now)
    check("the fill happened", st["filed"] == ["one.json"])
    check("and the job it just filed is not called a wedge",
          not st["drainer"]["stalled"])


def test_every_number_in_the_payload_describes_one_instant(root):
    """The payload's counts must agree with the DIRECTORIES, at a stated instant.

    Observed 2026-08-16 10:16Z: `--status` printed drainer {"ready": 0,
    "running": 0} and backlog_remaining 1 while the box's own directories held
    3 ready, 1 running, 6 backlog. Nothing was mis-globbed, nothing was cached,
    no path was remote-vs-local confused: `ready_jobs`, `ready_minutes`,
    `ready_kinds`, `running_jobs` and every field of `drainer` were read BEFORE
    the fill and then published under an `at` stamped AFTER it, so a tick that
    filed four jobs published the count from before those four existed. The
    `why` string escaped only because it spells out both instants itself.

    This case is that tick exactly: an empty queue, one claimed job, four LTX
    entries in the backlog -- "filed 4, now 22.8 min".
    """
    write(root, "running", "live.json", job("live"))
    write(root, "", "runner.log", "x")
    for i in range(4):
        write(root, "backlog", "b%d.json" % i, job("b%d" % i))
    st = af.tick(root)
    check("the fill happened, four jobs", len(st["filed"]) == 4)

    # The directory listing is ground truth. The tool agrees with it, never the
    # other way round -- so these are read fresh, not taken from the payload.
    truth_ready = len(af.json_names(os.path.join(root, "ready")))
    truth_running = len(af.json_names(os.path.join(root, "running")))
    truth_backlog = len(af.json_names(os.path.join(root, "backlog")))
    check("the tree really holds 4 ready, 1 running, 0 backlog",
          (truth_ready, truth_running, truth_backlog) == (4, 1, 0))

    check("ready_jobs_after equals the ready/ listing",
          st.get("ready_jobs_after") == truth_ready)
    check("running_jobs_after equals the running/ listing",
          st.get("running_jobs_after") == truth_running)
    check("backlog_remaining equals the backlog/ listing",
          st["backlog_remaining"] == truth_backlog)
    check("backlog_jobs_after equals it too", st.get("backlog_jobs_after") == truth_backlog)
    check("ready_minutes_after is MEASURED off ready/, not predicted forward",
          st.get("ready_minutes_after") == af.queue_minutes(root, "ready")[0])
    check("ready_kinds_after describes the queue that now exists",
          st.get("ready_kinds_after") == {"ltx": 4})

    # The pre-fill reading is what the DECISION was made on and is still wanted
    # -- but it may only be published under a name that says so.
    check("the pre-fill depth is kept, under a _before name",
          st.get("ready_jobs_before") == 0 and st.get("ready_minutes_before") == 0.0)
    check("no bare 'ready_jobs' survives to be misread as now",
          "ready_jobs" not in st and "running_jobs" not in st
          and "ready_minutes" not in st and "ready_kinds" not in st)
    check("the drainer's evidence is labelled pre-fill too",
          st["drainer"].get("ready_jobs_before") == 0
          and st["drainer"].get("running_jobs_before") == 1
          and "ready" not in st["drainer"] and "running" not in st["drainer"])
    b, a = st.get("measured_before_at"), st.get("measured_after_at")
    check("each phase carries its own stamp",
          isinstance(b, str) and isinstance(a, str) and b <= a == st["at"])


def test_a_no_op_tick_still_agrees_with_the_directories(root):
    """When nothing is filed, before and after must be the same numbers."""
    write(root, "", "runner.log", "x")
    for i in range(9):
        write(root, "ready", "r%d.json" % i, job("r%d" % i))
    st = af.tick(root)
    check("a full queue files nothing", st["status"] == "full" and st["filed"] == [])
    check("before and after agree when nothing moved",
          st.get("ready_jobs_before") == st.get("ready_jobs_after") == 9
          and st.get("ready_minutes_before") == st.get("ready_minutes_after"))


def test_a_blocked_fill_reports_the_queue_that_actually_exists(root):
    """The green-tick bug, one level down: 'wanted 4' must not become 'has 4'."""
    write(root, "", "runner.log", "x")
    for i in range(4):
        write(root, "backlog", "b%d.json" % i, job("b%d" % i))
    real_rename = os.rename
    try:
        os.rename = lambda *a, **k: (_ for _ in ()).throw(OSError("locked"))
        st = af.tick(root)
    finally:
        os.rename = real_rename
    check("a fill where every move failed is not 'filled'", st["status"] == "blocked")
    check("and the after-count is the empty queue that really exists",
          st.get("ready_jobs_after") == 0 and st.get("ready_minutes_after") == 0.0)
    check("and the backlog it failed to drain is still four",
          st["backlog_remaining"] == 4)


def test_status_reconciles_the_snapshot_against_the_live_listing():
    """--status must never hand a stale count over as the truth of now.

    The payload is written by a tick up to three minutes ago; the founder's
    question is about this second. `reconcile` is the pure half of --status:
    given the snapshot and a live listing, does it say they disagree?
    """
    st = {"at": "2026-08-16T10:16:01Z", "ready_jobs_after": 4,
          "running_jobs_after": 0, "backlog_remaining": 1}
    live = {"ready": 3, "running": 1, "backlog": 6}
    lines, disagrees = af.reconcile(st, live)
    body = "\n".join(lines)
    check("it prints the live listing as its own row", "3" in body and "6" in body)
    check("a backlog that grew since the tick is called out", disagrees)
    check("and the disagreement names the field", "backlog" in body)
    same, ok = af.reconcile(st, {"ready": 4, "running": 0, "backlog": 1})
    check("an agreeing pair is not flagged", not ok)


def test_a_gate_refusal_is_propagated_not_swallowed(tmp):
    spec = {"id": "gated-1786800000", "consumer": "a test",
            "gate": "founder must screen the b06 sample first",
            "steps": [{"argv": ["python", "ltx_i2v.py"]}]}
    path = os.path.join(tmp, "gated.json")
    with open(path, "w") as fh:
        json.dump(spec, fh)
    rc = be.main([path, "--backlog", "--dry-run"])
    check("a spec carrying gate: cannot be filed to the backlog", rc == 1)


def test_a_plate_ack_waiver_cannot_be_backlogged(tmp):
    spec = {"id": "waived-1786800000", "consumer": "a test",
            "plate_ack": "card: a deliberate macro close-up of the fruit",
            "steps": [{"argv": ["python", "ltx_i2v.py", "--src", "x.png"]}]}
    path = os.path.join(tmp, "waived.json")
    with open(path, "w") as fh:
        json.dump(spec, fh)
    problems = be.backlog_problems(spec)
    check("a waived spec is refused at the backlog door", len(problems) == 1)
    check("and the refusal says which waiver", "plate_ack" in problems[0])
    rc = be.main([path, "--backlog", "--dry-run"])
    check("so --backlog exits nonzero on it", rc == 1)
    check("while the same spec is still enqueueable by hand",
          be.backlog_problems({"id": "x"}) == [])


def test_a_clean_spec_is_stamped_with_its_filing_time():
    j = be.with_backlog_meta({"id": "x"}, "pipeline/jobs/x.yaml", 12.0)
    check("the entry carries when it was filed", j["backlog"]["filed_at"] > 0)
    check("and how long it stays true", j["backlog"]["expires_h"] == 12.0)
    check("and box_autofill reads that life back", af.expires_hours(j) == 12.0)


def test_a_backlogged_job_still_owns_its_payload_paths():
    """The listing the collision guard reads must include backlog/."""
    src = be.queued_job_ids.__doc__ or ""
    check("queued_job_ids documents that backlog counts as live",
          "BACKLOG COUNTS AS LIVE" in src)
    ids = be.parse_queue_listing("a.json\nb.json\n" + be.QUEUE_MARKER)
    check("and it still parses a listing", ids == {"a", "b"})


def main():
    print("box_autofill — depth, backlog and the guards on the way in")
    cases = [test_hold_files_are_not_depth, test_depth_is_minutes_not_jobs,
             test_running_is_not_counted_as_ready_depth,
             test_an_unreadable_ready_file_is_not_worth_zero,
             test_the_tick_exits_2_when_it_is_hungry_with_nothing_to_draw,
             test_an_unstamped_entry_expires_off_its_mtime,
             test_a_refused_entry_keeps_its_bytes_and_says_why,
             test_a_real_tick_files_from_backlog_into_ready,
             test_a_dry_run_moves_nothing, test_it_never_unholds_a_parked_job,
             test_it_never_touches_a_running_job,
             test_a_job_id_in_ready_is_not_filed_twice,
             test_priority_order_is_the_runners_order,
             test_an_entry_with_no_clock_at_all_is_refused,
             test_a_wedged_drainer_is_not_reported_as_a_healthy_queue,
             test_a_stall_is_not_declared_over_a_live_or_quiet_card,
             test_filing_work_does_not_look_like_a_stall,
             test_a_fill_that_moved_nothing_does_not_report_filled,
             test_every_number_in_the_payload_describes_one_instant,
             test_a_no_op_tick_still_agrees_with_the_directories,
             test_a_blocked_fill_reports_the_queue_that_actually_exists]
    for fn in cases:
        with tempfile.TemporaryDirectory() as td:
            fn(td)
    for fn in (test_a_full_queue_is_left_alone, test_it_fills_only_up_to_the_floor,
               test_the_per_tick_cap_holds,
               test_an_empty_backlog_is_a_loud_state_not_an_invention,
               test_backlog_exhaustion_mid_fill,
               test_a_superseded_entry_is_never_refiled,
               test_an_expired_entry_is_not_fired,
               test_a_clean_spec_is_stamped_with_its_filing_time,
               test_a_backlogged_job_still_owns_its_payload_paths,
               test_status_reconciles_the_snapshot_against_the_live_listing):
        fn()
    for fn in (test_a_gate_refusal_is_propagated_not_swallowed,
               test_a_plate_ack_waiver_cannot_be_backlogged):
        with tempfile.TemporaryDirectory() as td:
            fn(td)
    print()
    if FAILURES:
        print("✗ %d failure(s): %s" % (len(FAILURES), ", ".join(FAILURES)))
        return 1
    print("✓ all box_autofill cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
