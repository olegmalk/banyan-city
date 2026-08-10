#!/usr/bin/env python3
"""Pure-logic tests for the box-resident render runner.

No GPU, no network, no Windows: every test drives box_runner against a temp
queue root with steps that are plain python one-liners. What is under test is
the part that has to be right when nobody is watching -- the claim being atomic,
an interrupted job being retired honestly exactly once, the lock surviving a
reboot-pid-collision, and the GPU claim file never being stolen from a hand lane.

Run: python3 pipeline/test_box_runner.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import box_runner as br  # noqa: E402

FAILURES = []
PASSED = 0


def check(cond, label):
    global PASSED
    if cond:
        PASSED += 1
    else:
        FAILURES.append(label)


def eq(got, want, label):
    check(got == want, "%s: got %r want %r" % (label, got, want))


class TempRoot:
    def __enter__(self):
        self.path = tempfile.mkdtemp(prefix="boxq-")
        for sub in br.SUBDIRS:
            os.makedirs(os.path.join(self.path, sub), exist_ok=True)
        return self.path

    def __exit__(self, *exc):
        shutil.rmtree(self.path, ignore_errors=True)


def job(jid, steps, **kw):
    d = {"id": jid, "steps": steps, "needs_gpu": False}
    d.update(kw)
    return d


def py_step(name, code, **kw):
    d = {"name": name, "argv": [sys.executable, "-c", code]}
    d.update(kw)
    return d


def enqueue(root, spec):
    br.write_json(os.path.join(root, "ready", spec["id"] + ".json"), spec)


def drain(root, **kw):
    argv = ["--root", root, "--once", "--poll", "0", "--no-courier"]
    for k, v in kw.items():
        argv += ["--" + k.replace("_", "-"), str(v)]
    return br.main(argv)


def listing(root, sub):
    return sorted(os.listdir(os.path.join(root, sub)))


def beats(root):
    path = os.path.join(root, "heartbeats.jsonl")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


# ---------------------------------------------------------------------------

def test_happy_path():
    with TempRoot() as root:
        art = os.path.join(root, "made.txt")
        enqueue(root, job("j-ok", [
            py_step("write", "open(%r,'w').write('hi')" % art),
        ], artifacts=[art]))
        rc = drain(root)
        eq(rc, 0, "happy: main rc")
        eq(listing(root, "ready"), [], "happy: ready drained")
        eq(listing(root, "running"), [], "happy: running empty")
        eq(listing(root, "done"), ["j-ok.json", "j-ok.log"], "happy: done holds job+log")
        check(os.path.exists(art), "happy: artifact written")
        with open(os.path.join(root, "done", "j-ok.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        eq(rec["rc"], 0, "happy: recorded rc")
        eq(rec["attempts"], 1, "happy: one attempt")
        events = [b["event"] for b in beats(root)]
        check("job_start" in events and "job_done" in events, "happy: start+done beat")


def test_failing_step_stops_the_job():
    with TempRoot() as root:
        later = os.path.join(root, "should-not-exist.txt")
        enqueue(root, job("j-fail", [
            py_step("boom", "import sys; sys.exit(3)"),
            py_step("after", "open(%r,'w').write('x')" % later),
        ]))
        drain(root)
        eq(listing(root, "failed"), ["j-fail.json", "j-fail.log"], "fail: retired to failed/")
        check(not os.path.exists(later), "fail: later step did not run")
        with open(os.path.join(root, "failed", "j-fail.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        eq(rec["rc"], 3, "fail: rc preserved")
        eq(rec["failed_step"], "boom", "fail: names the step")


def test_allow_fail_continues():
    with TempRoot() as root:
        art = os.path.join(root, "after.txt")
        enqueue(root, job("j-af", [
            py_step("soft", "import sys; sys.exit(9)", allow_fail=True),
            py_step("after", "open(%r,'w').write('x')" % art),
        ], artifacts=[art]))
        drain(root)
        eq(listing(root, "done"), ["j-af.json", "j-af.log"], "allow_fail: still done")
        check(os.path.exists(art), "allow_fail: later step ran")


def test_missing_artifact_fails_a_zero_rc_job():
    """A job whose steps all succeed but which produced nothing is a failure.

    This is the check that stops a silently-broken render from being reported as
    a finished one -- the whole point of naming artifacts in the job file.
    """
    with TempRoot() as root:
        enqueue(root, job("j-noart", [py_step("nop", "pass")],
                          artifacts=[os.path.join(root, "never.mp4")]))
        drain(root)
        eq(listing(root, "failed"), ["j-noart.json", "j-noart.log"], "artifact: failed")
        with open(os.path.join(root, "failed", "j-noart.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        eq(rec["rc"], 92, "artifact: rc 92")
        eq(rec["failed_step"], "artifact-check", "artifact: named step")


def test_priority_then_name_order():
    with TempRoot() as root:
        log = os.path.join(root, "order.txt")
        code = "open(%r,'a').write('%%s ')" % log
        enqueue(root, job("b-mid", [py_step("s", code % "mid")], priority=50))
        enqueue(root, job("a-late", [py_step("s", code % "late")], priority=90))
        enqueue(root, job("c-first", [py_step("s", code % "first")], priority=1))
        drain(root)
        with open(log, encoding="utf-8") as fh:
            eq(fh.read().split(), ["first", "mid", "late"], "order: priority wins over name")


def test_interrupted_job_is_retired_not_rerun():
    """A job left in running/ by a dead runner must not silently run again."""
    with TempRoot() as root:
        spec = job("j-int", [py_step("s", "pass")], attempts=1, max_attempts=1)
        br.write_json(os.path.join(root, "running", "j-int.json"), spec)
        drain(root)
        eq(listing(root, "failed"), ["j-int.json"], "interrupt: retired to failed/")
        eq(listing(root, "ready"), [], "interrupt: not requeued")
        with open(os.path.join(root, "failed", "j-int.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        eq(rec["rc"], 93, "interrupt: rc 93")
        check(rec["interrupted"] is True, "interrupt: flagged")


def test_interrupted_job_requeues_when_it_opted_in():
    with TempRoot() as root:
        art = os.path.join(root, "retry.txt")
        spec = job("j-retry", [py_step("s", "open(%r,'w').write('x')" % art)],
                   attempts=1, max_attempts=3, artifacts=[art])
        br.write_json(os.path.join(root, "running", "j-retry.json"), spec)
        drain(root)
        eq(listing(root, "done"), ["j-retry.json", "j-retry.log"], "requeue: ran and finished")
        with open(os.path.join(root, "done", "j-retry.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        eq(rec["attempts"], 2, "requeue: attempt count carried forward")


def test_unreadable_job_fails_without_killing_the_runner():
    with TempRoot() as root:
        with open(os.path.join(root, "ready", "j-junk.json"), "w") as fh:
            fh.write("{not json")
        art = os.path.join(root, "good.txt")
        enqueue(root, job("j-good", [py_step("s", "open(%r,'w').write('x')" % art)],
                          artifacts=[art], priority=200))
        eq(drain(root), 0, "junk: runner survived")
        eq(listing(root, "failed"), ["j-junk.json"], "junk: retired")
        check(os.path.exists(art), "junk: later job still ran")


def test_step_with_no_argv_is_a_clean_failure():
    with TempRoot() as root:
        enqueue(root, job("j-noargv", [{"name": "empty"}]))
        eq(drain(root), 0, "noargv: runner survived")
        with open(os.path.join(root, "failed", "j-noargv.json"), encoding="utf-8") as fh:
            eq(json.load(fh)["rc"], 90, "noargv: rc 90")


def test_env_reaches_the_step():
    with TempRoot() as root:
        out = os.path.join(root, "env.txt")
        code = ("import os;open(%r,'w').write(os.environ.get('JOB_V','')+'/'"
                "+os.environ.get('STEP_V',''))" % out)
        enqueue(root, job("j-env", [py_step("s", code, env={"STEP_V": "step"})],
                          env={"JOB_V": "job"}, artifacts=[out]))
        drain(root)
        with open(out, encoding="utf-8") as fh:
            eq(fh.read(), "job/step", "env: job env and step env both applied")


def test_max_jobs_stops_after_n():
    with TempRoot() as root:
        for i in range(3):
            enqueue(root, job("j-%d" % i, [py_step("s", "pass")], priority=i))
        drain(root, max_jobs=2)
        eq(len(listing(root, "done")), 4, "max_jobs: two jobs (json+log each)")
        eq(listing(root, "ready"), ["j-2.json"], "max_jobs: remainder left queued")


# -- lock -------------------------------------------------------------------

def test_lock_excludes_a_second_runner():
    with TempRoot() as root:
        path = os.path.join(root, "runner.lock")
        with open(path, "w") as fh:
            fh.write("%d %s boot=%d\n" % (os.getppid() or 1, br.utcnow(), br.boot_id()))
        check(not br.acquire_lock(path), "lock: live holder blocks")


def test_lock_from_a_previous_boot_is_stale():
    """The reboot case: the same pid handed out again after a restart.

    boot_id() is patched rather than read, because it returns 0 on macOS (no
    /proc/stat, not Windows) -- which would make this pass by accident here and
    still be wrong on the box, where the whole scenario actually happens.
    """
    real = br.boot_id
    try:
        br.boot_id = lambda: 1_700_000_000
        live_pid = os.getppid() or 1
        # same boot, live pid -> the lock IS live
        check(br.lock_is_live(live_pid, 1_700_000_000), "lock: same boot + live pid is live")
        # earlier boot, same pid -> stale no matter what the OS says about the pid
        check(not br.lock_is_live(live_pid, 1_699_000_000),
              "lock: pre-reboot lock is stale even with a live pid")
        with TempRoot() as root:
            path = os.path.join(root, "runner.lock")
            with open(path, "w") as fh:
                fh.write("%d %s boot=1699000000\n" % (live_pid, br.utcnow()))
            check(br.acquire_lock(path), "lock: pre-reboot lock reclaimed")
            holder, boot = br.read_lock(path)
            eq(holder, os.getpid(), "lock: we own it now")
            eq(boot, 1_700_000_000, "lock: our boot id recorded")
            br.release_lock(path)
            check(not os.path.exists(path), "lock: released")
    finally:
        br.boot_id = real


def test_lock_from_a_dead_pid_is_reclaimed():
    with TempRoot() as root:
        path = os.path.join(root, "runner.lock")
        with open(path, "w") as fh:
            fh.write("999999 %s boot=%d\n" % (br.utcnow(), br.boot_id()))
        check(br.acquire_lock(path), "lock: dead pid reclaimed")


def test_garbage_lock_is_reclaimed():
    with TempRoot() as root:
        path = os.path.join(root, "runner.lock")
        with open(path, "w") as fh:
            fh.write("this is not a pid\n")
        check(br.acquire_lock(path), "lock: unparseable lock reclaimed")


def test_release_does_not_steal_another_runners_lock():
    with TempRoot() as root:
        path = os.path.join(root, "runner.lock")
        with open(path, "w") as fh:
            fh.write("424242 %s boot=%d\n" % (br.utcnow(), br.boot_id()))
        br.release_lock(path)
        check(os.path.exists(path), "lock: foreign lock left alone")


def test_second_runner_exits_75():
    with TempRoot() as root:
        os.makedirs(os.path.join(root, "ready"), exist_ok=True)
        path = os.path.join(root, "runner.lock")
        with open(path, "w") as fh:
            fh.write("%d %s boot=%d\n" % (os.getppid() or 1, br.utcnow(), br.boot_id()))
        eq(drain(root), 75, "lock: second runner returns 75")


# -- GPU claim --------------------------------------------------------------

def test_claim_file_semantics():
    check(not br.claim_is_foreign(""), "claim: absent means free")
    check(not br.claim_is_foreign("RELEASED by card-runner-3 at now"), "claim: RELEASED is free")
    check(br.claim_is_foreign("HELD by card-runner-3 job=v34"), "claim: hand lane is foreign")
    check(not br.claim_is_foreign("HELD by box-runner job=x"), "claim: our own is not foreign")


def test_claim_round_trip_and_no_theft():
    with TempRoot() as root:
        path = os.path.join(root, "GPU-CLAIM.txt")
        br.take_claim("j-1", path)
        check("HELD by box-runner" in br.read_claim(path), "claim: taken")
        br.drop_claim("j-1", path)
        check("RELEASED" in br.read_claim(path), "claim: released")
        with open(path, "w") as fh:
            fh.write("HELD by card-runner-3 job=v34-b06\n")
        br.drop_claim("j-1", path)
        eq(br.read_claim(path), "HELD by card-runner-3 job=v34-b06",
           "claim: a hand lane's claim is never released by us")


# -- courier ----------------------------------------------------------------

def test_quiet_events_are_thinned_but_job_events_never_are():
    q = br.Queue.__new__(br.Queue)
    q._last_quiet_push = 0.0
    check(q.quiet_push_due("job_done", now=1000), "quiet: job events always ship")
    check(q.quiet_push_due("runner_idle", now=1000), "quiet: first idle ships")
    check(not q.quiet_push_due("runner_idle", now=1060), "quiet: second idle thinned")
    check(q.quiet_push_due("runner_idle", now=1000 + br.COURIER_IDLE_MINUTES * 60 + 1),
          "quiet: ships again after the window")
    check(q.quiet_push_due("job_start", now=1061), "quiet: job start still ships")


def test_courier_emits_farm_worker_grammar():
    """The lines must parse as farm_worker's, or every reader misses the job."""
    seen = []

    class FakeCourier(br.Courier):
        def __init__(self):
            br.Courier.__init__(self, "/nope", "b", "/nope")

        def mark(self, line, message, files=None):
            seen.append(line)

    c = FakeCourier()
    c.emit({"event": "job_start", "job": "j-1", "attempt": 1})
    c.emit({"event": "job_done", "job": "j-1", "artifacts": ["a.mp4"]})
    c.emit({"event": "job_failed", "job": "j-2", "rc": 3, "failed_step": "render"})
    check(seen[0].startswith("STARTED task=j-1"), "grammar: STARTED task=<id>")
    check(seen[1].startswith("DONE task=j-1"), "grammar: DONE task=<id>")
    check(seen[2].startswith("FAIL task=j-2"), "grammar: FAIL task=<id>")


def test_courier_failure_never_reaches_the_runner():
    """A courier that raises must not stop a render. Job still lands as done."""
    class Exploding(br.Courier):
        def __init__(self):
            br.Courier.__init__(self, "/nope", "b", "/nope")

        def ensure(self):
            raise RuntimeError("network is on fire")

    with TempRoot() as root:
        q = br.Queue(root, courier=Exploding())
        art = os.path.join(root, "a.txt")
        spec = job("j-c", [py_step("s", "open(%r,'w').write('x')" % art)], artifacts=[art])
        path = os.path.join(root, "running", "j-c.json")
        br.write_json(path, spec)
        outcome, rc, _ = br.execute(spec, path, q)
        eq(outcome, "done", "courier: render unaffected by courier explosion")
        eq(rc, 0, "courier: rc 0")
        check(len(beats(root)) >= 2, "courier: local heartbeats still written")


def test_courier_is_off_when_asked():
    with TempRoot() as root:
        enqueue(root, job("j-nc", [py_step("s", "pass")]))
        eq(drain(root), 0, "no-courier: drains fine")


# -- misc -------------------------------------------------------------------

def test_write_json_is_atomic_and_leaves_no_tmp():
    with TempRoot() as root:
        p = os.path.join(root, "x.json")
        br.write_json(p, {"a": 1})
        eq(json.load(open(p)), {"a": 1}, "write_json: round trip")
        check(not os.path.exists(p + ".tmp"), "write_json: no tmp left behind")


def test_tail_text_never_raises():
    check("unreadable" in br.tail_text("/definitely/not/here.log"), "tail: missing file handled")


def test_queue_creates_its_layout():
    with TempRoot() as root:
        sub = os.path.join(root, "fresh")
        br.Queue(sub)
        for d in br.SUBDIRS:
            check(os.path.isdir(os.path.join(sub, d)), "layout: %s created" % d)


def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for fn in tests:
        try:
            fn()
        except Exception:
            FAILURES.append("%s RAISED\n%s" % (fn.__name__, traceback.format_exc()))
    print("box_runner: %d checks passed, %d failed" % (PASSED, len(FAILURES)))
    for f in FAILURES:
        print("  FAIL " + f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
