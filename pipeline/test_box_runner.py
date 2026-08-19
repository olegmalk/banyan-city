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
import time
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


def test_the_runner_verdicts_never_share_a_code():
    """The rc table's one invariant: no two verdicts spell themselves alike.

    An rc is the runner's whole answer to "what do I do about this?", and the
    answers are minutes apart from hours apart. On 2026-08-14 "published
    nothing" and "render crashed" were both 92 and six good plates were retired
    as crashes. The fix gave published-nothing its own code -- but reached for
    93, which adopt_interrupted already owned, so the ambiguity merely moved to
    {interrupted, published nothing} and CI went red.

    This check is deliberately about the PROPERTY, not the numbers: renumber the
    table freely, collapse any two of them and this fails.
    """
    codes = {
        "step declares no argv": br.RC_STEP_NO_ARGV,
        "step raised in the runner": br.RC_STEP_RAISED,
        "some artifacts missing": br.RC_ARTIFACTS_MISSING,
        "interrupted mid-render": br.RC_INTERRUPTED,
        "job json unreadable": br.RC_JOB_UNREADABLE,
        "published nothing": br.RC_PUBLISHED_NOTHING,
    }
    eq(len(set(codes.values())), len(codes),
       "rc table: every verdict has a code of its own (%r)" % (codes,))
    check(all(v >= 90 for v in codes.values()),
          "rc table: runner verdicts stay out of the steps' own exit range")
    # The three the 2026-08-14/15 defect ran together, named one more time so a
    # reader of a failure sees which pair collapsed.
    check(br.RC_ARTIFACTS_MISSING != br.RC_PUBLISHED_NOTHING,
          "rc table: a crashed render is not a job that published nothing")
    check(br.RC_INTERRUPTED != br.RC_PUBLISHED_NOTHING,
          "rc table: an interrupted runner is not a job that published nothing")
    check(br.RC_ARTIFACTS_MISSING != br.RC_INTERRUPTED,
          "rc table: a crashed render is not an interrupted runner")


def test_publishing_nothing_is_its_own_verdict():
    """All steps exited 0 and NOT ONE declared artifact landed.

    Not a crash: a wrong publish glob or a wrong artifacts declaration. Fixed by
    re-publishing in seconds, so it must not read as the ninety-minute failure.
    """
    with TempRoot() as root:
        enqueue(root, job("j-noart", [py_step("nop", "pass")],
                          artifacts=[os.path.join(root, "never.mp4")]))
        drain(root)
        eq(listing(root, "failed"), ["j-noart.json", "j-noart.log"], "publish-empty: failed")
        with open(os.path.join(root, "failed", "j-noart.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        eq(rec["rc"], br.RC_PUBLISHED_NOTHING, "publish-empty: its own rc")
        eq(rec["failed_step"], "publish-empty", "publish-empty: named step")
        check(rec["rc"] != br.RC_ARTIFACTS_MISSING,
              "publish-empty: not spelled like a partial render")
        check(rec["rc"] != br.RC_INTERRUPTED,
              "publish-empty: not spelled like an interrupted runner")


def test_missing_artifact_fails_a_zero_rc_job():
    """A job whose steps all succeed but which produced only SOME of what it
    declared is a failure, and a different one from publishing nothing.

    This is the check that stops a silently-broken render from being reported as
    a finished one -- the whole point of naming artifacts in the job file.
    """
    with TempRoot() as root:
        landed = os.path.join(root, "landed.txt")
        enqueue(root, job("j-part", [py_step("half", "open(%r,'w').write('x')" % landed)],
                          artifacts=[landed, os.path.join(root, "never.mp4")]))
        drain(root)
        eq(listing(root, "failed"), ["j-part.json", "j-part.log"], "artifact: failed")
        with open(os.path.join(root, "failed", "j-part.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        eq(rec["rc"], br.RC_ARTIFACTS_MISSING, "artifact: rc 92")
        eq(rec["failed_step"], "artifact-check", "artifact: named step")
        check(rec["rc"] != br.RC_PUBLISHED_NOTHING,
              "artifact: a partial landing is not 'published nothing'")


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
        eq(rec["rc"], br.RC_INTERRUPTED, "interrupt: rc 93")
        eq(rec["failed_step"], "interrupted", "interrupt: named step")
        check(rec["interrupted"] is True, "interrupt: flagged")
        check(rec["rc"] != br.RC_PUBLISHED_NOTHING,
              "interrupt: not spelled like a job that published nothing")


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
        # The job file is junk, so its verdict exists only in the heartbeat.
        junk = [b for b in beats(root)
                if b.get("event") == "job_failed" and b.get("job") == "j-junk"]
        eq([b["rc"] for b in junk], [br.RC_JOB_UNREADABLE], "junk: rc 94")
        check(br.RC_JOB_UNREADABLE not in (br.RC_PUBLISHED_NOTHING, br.RC_INTERRUPTED),
              "junk: unparseable is not published-nothing or interrupted")


def test_step_with_no_argv_is_a_clean_failure():
    with TempRoot() as root:
        enqueue(root, job("j-noargv", [{"name": "empty"}]))
        eq(drain(root), 0, "noargv: runner survived")
        with open(os.path.join(root, "failed", "j-noargv.json"), encoding="utf-8") as fh:
            eq(json.load(fh)["rc"], br.RC_STEP_NO_ARGV, "noargv: rc 90")


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


def test_the_claim_file_is_not_invented_on_a_non_windows_box():
    """GPU_CLAIM_FILE is a Windows absolute path and a POSIX RELATIVE one.

    So every default-path claim call on a Mac read and wrote a file literally
    named `C:\\banyan-farm\\GPU-CLAIM.txt` in the cwd. Running this suite from a
    checkout left one untracked in the repo root — one `git add -A` from being
    committed — and read_claim would have believed a stale HELD line in it.
    """
    if os.name == "nt":
        eq(br._claim_path(), br.GPU_CLAIM_FILE, "claim: Windows uses the real path")
    else:
        check(br._claim_path() is None, "claim: no claim convention off Windows")
        eq(br.read_claim(), "", "claim: and the default read is empty, not a file")
        before = os.path.isfile(br.GPU_CLAIM_FILE)
        br.take_claim("j-1")
        br.drop_claim("j-1")
        eq(os.path.isfile(br.GPU_CLAIM_FILE), before,
           "claim: and no C:\\... file is created in the cwd")
    eq(br._claim_path("/tmp/explicit"), "/tmp/explicit",
       "claim: an explicit path is always honoured")


def test_an_unreadable_claim_file_is_not_an_absent_one():
    """A claim we cannot read must not be spelled the same way as no claim.

    read_claim() caught every OSError and returned "", so a permission error or a
    dead network path on GPU-CLAIM.txt read as "the card is free" -- and that is
    the one file that catches a hand lane which has claimed the card and is still
    in LTX's several-minute encode stage, where no process or VRAM probe can see
    it. Missing is still "", because a missing file genuinely means nobody has
    claimed the card.
    """
    with TempRoot() as root:
        missing = os.path.join(root, "no-such-claim.txt")
        eq(br.read_claim(missing), "", "claim: a missing file is genuinely free")
        check(not br.claim_is_foreign(br.read_claim(missing)),
              "claim: a missing file does not block the runner")

        # a directory where the file should be: open() raises IsADirectoryError
        # (an OSError that is not FileNotFoundError), the same shape a permission
        # error or an unreachable UNC path takes
        blocked = os.path.join(root, "blocked-claim.txt")
        os.makedirs(blocked)
        text = br.read_claim(blocked)
        check(br.CLAIM_UNREADABLE in text, "claim: an unreadable file says so")
        check(br.claim_is_foreign(text),
              "claim: an unreadable claim counts as held, not as free")


# -- probe failures must not read as a free card ----------------------------

def test_a_failed_process_probe_counts_as_a_busy_card():
    """powershell not answering is not the same fact as "nothing is rendering".

    _foreign_render_processes() returned [] on any exception, which gpu_busy()
    read as "no foreign render" and passed straight through to the VRAM probe.
    Two probes down and the third also failing open meant the runner would claim
    the card and start a second render on top of a live one -- the documented
    way this box earns a WDDM-thrash bugcheck.
    """
    # read_claim is pinned too: the claim path is absolute-on-Windows and
    # therefore RELATIVE on this Mac, so a stray file of that name in the cwd
    # would decide these assertions instead of the probe under test.
    real, real_claim = br._foreign_render_processes, br.read_claim
    try:
        br.read_claim = lambda path=None: ""
        br._foreign_render_processes = lambda: None
        busy, why = br.gpu_busy()
        check(busy, "probe: a failed process probe is busy")
        check("process probe FAILED" in why, "probe: the reason names the probe")

        br._foreign_render_processes = lambda: []
        real_vram = br._gpu_vram_mib
        try:
            br._gpu_vram_mib = lambda: 0
            busy, why = br.gpu_busy()
            check(not busy, "probe: both probes answering free means free")
        finally:
            br._gpu_vram_mib = real_vram
    finally:
        br._foreign_render_processes, br.read_claim = real, real_claim


def test_a_failed_vram_probe_counts_as_a_busy_card():
    """nvidia-smi timing out returned 0 MiB -- the empty-card number.

    And the other half, which is what makes this safe to ship: nvidia-smi being
    ABSENT is not doubt, it is a machine without an NVIDIA card. Conflating the
    two wedges every Mac and every CI runner shut -- the first cut of this fix
    did exactly that and left the box suite waiting for a GPU on a laptop.
    """
    real_proc, real_vram = br._foreign_render_processes, br._gpu_vram_mib
    real_claim = br.read_claim
    try:
        br.read_claim = lambda path=None: ""
        br._foreign_render_processes = lambda: []

        br._gpu_vram_mib = lambda: br.VRAM_PROBE_FAILED
        busy, why = br.gpu_busy()
        check(busy, "probe: nvidia-smi present but silent is busy")
        check("VRAM probe FAILED" in why, "probe: the reason names the probe")

        br._gpu_vram_mib = lambda: br.VRAM_PROBE_UNAVAILABLE
        busy, why = br.gpu_busy()
        check(not busy, "probe: no nvidia-smi on this machine is not doubt")

        br._gpu_vram_mib = lambda: br.GPU_BUSY_VRAM_MIB + 1
        busy, _ = br.gpu_busy()
        check(busy, "probe: a loaded card is still busy")
    finally:
        br._foreign_render_processes, br._gpu_vram_mib = real_proc, real_vram
        br.read_claim = real_claim


def test_the_vram_probe_tells_absent_apart_from_broken():
    """The sentinel each real failure maps to, driven through subprocess.run."""
    real_run = br.subprocess.run
    try:
        def missing(*a, **kw):
            raise FileNotFoundError(2, "No such file or directory", "nvidia-smi")
        br.subprocess.run = missing
        eq(br._gpu_vram_mib(), br.VRAM_PROBE_UNAVAILABLE,
           "vram: a machine with no nvidia-smi says UNAVAILABLE")

        def timeout(*a, **kw):
            raise br.subprocess.TimeoutExpired(cmd="nvidia-smi", timeout=30)
        br.subprocess.run = timeout
        eq(br._gpu_vram_mib(), br.VRAM_PROBE_FAILED,
           "vram: a timeout says FAILED, never 0 MiB")

        class R:
            def __init__(self, rc, out):
                self.returncode, self.stdout = rc, out
        br.subprocess.run = lambda *a, **kw: R(9, "")
        eq(br._gpu_vram_mib(), br.VRAM_PROBE_FAILED, "vram: a nonzero exit says FAILED")
        br.subprocess.run = lambda *a, **kw: R(0, "")
        eq(br._gpu_vram_mib(), br.VRAM_PROBE_FAILED, "vram: empty output says FAILED")
        br.subprocess.run = lambda *a, **kw: R(0, "1024\n7\n")
        eq(br._gpu_vram_mib(), 1024, "vram: a real reading is the busiest card")
    finally:
        br.subprocess.run = real_run


def test_an_unreadable_failed_dir_does_not_report_zero_failures():
    """The corpse-counting guard must not have the same hole one level down."""
    with TempRoot() as root:
        q = br.Queue(root)
        eq(q.failed_count(), 0, "failed: an empty dir is genuinely zero")
        shutil.rmtree(q.dir("failed"))
        # a FILE where the failed/ directory should be: listdir raises
        with open(q.dir("failed"), "w") as fh:
            fh.write("not a directory")
        eq(q.failed_count(), -1,
           "failed: an uncountable dir reports -1, never a healthy 0")


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

        def mark(self, line, message, files=None, push=True):
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


# -- courier: what a heartbeat is allowed to cost a render -------------------
#
# All four pin the 2026-08-18 defect: heartbeat pushes were synchronous, 300 s,
# fired on runner_up and job_start (both sitting directly in front of work), and
# left orphaned git children behind. Measured cost: ~8 min claim-to-first-step
# twice, 40 timeouts in a day, two runner deaths.

class RecordingCourier(br.Courier):
    """A courier whose worktree is real but whose push is a counter."""

    def __init__(self, out_dir):
        br.Courier.__init__(self, out_dir, "b", "/nope")
        self.published = []
        self.ready = True          # skip `git worktree add`

    def _publish(self, message):
        self.published.append(message)


def test_the_two_events_that_sit_in_front_of_work_do_not_push():
    with TempRoot() as root:
        c = RecordingCourier(root)
        c.emit({"event": "runner_up", "pid": 1, "host": "box"})
        c.emit({"event": "job_start", "job": "j-1", "attempt": 1})
        eq(c.published, [], "defer: runner_up and job_start push nothing")
        c.emit({"event": "job_done", "job": "j-1", "artifacts": ["a.mp4"]})
        eq(c.published, ["hb: DONE j-1"], "defer: job_done is what ships")

        # ...and the deferred lines are IN the worktree, in order, so the DONE
        # publish (`git add -A -- farm-out`) carries them out.
        with open(os.path.join(root, "farm-out", "heartbeat.txt"), encoding="utf-8") as fh:
            body = fh.read()
        check("box-runner up" in body, "defer: runner_up line was still written")
        check(body.index("STARTED task=j-1") < body.index("DONE task=j-1"),
              "defer: STARTED is on disk, before DONE, for the next push")


def test_liveness_and_verdict_events_still_push():
    """The deny list must not go wider than the two measured offenders.

    runner_idle is this box's only "still alive" signal (build_sim gives a
    machine 45 min); Queue.quiet_push_due already thins it to one per
    COURIER_IDLE_MINUTES before it reaches emit, so emit must not thin it again.
    """
    with TempRoot() as root:
        c = RecordingCourier(root)
        for rec in ({"event": "job_failed", "job": "j-2", "rc": 3},
                    {"event": "job_requeued_after_interrupt", "job": "j-3"},
                    {"event": "runner_down", "jobs_completed": 2},
                    {"event": "runner_idle", "ready": 0},
                    {"event": "runner_waiting_for_gpu", "reason": "vram"}):
            c.emit(rec)
        eq(len(c.published), 5, "deny list: every other event still ships")
        eq(br.DEFERRED_EVENTS, ("job_start", "runner_up"),
           "deny list: exactly the two measured offenders")


def test_a_push_that_hangs_is_bounded_and_does_not_wedge():
    """300 s of blocking per heartbeat was the whole latency bug."""
    check(br.PUSH_TIMEOUT_SECONDS <= 60, "push: hard timeout is <= 60s")
    with TempRoot() as root:
        c = RecordingCourier(root)
        t0 = time.time()
        rc, out = c._push(argv=[sys.executable, "-c", "import time; time.sleep(30)"],
                          timeout=2)
        elapsed = time.time() - t0
        eq(rc, br.PUSH_RC_TIMEOUT, "push: timeout has its own rc")
        check(elapsed < 20, "push: returned in %.1fs, not after the child" % elapsed)
        check("killed" in out, "push: says the tree was killed")


def test_a_timed_out_push_takes_its_grandchildren_with_it():
    """subprocess.run(timeout=) kills the direct child ONLY.

    `git push` spawns git-pack-objects and ssh; they survive that kill holding
    the stdout pipe they inherited, which is both the orphan pile seen in Task
    Manager on the box and why the communicate() after the kill can block with
    no timeout at all. The whole process tree has to go.
    """
    with TempRoot() as root:
        c = RecordingCourier(root)
        pidfile = os.path.join(root, "grandchild.pid").replace("\\", "\\\\")
        code = (
            "import subprocess, sys, time;"
            "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']);"
            "open(%r, 'w').write(str(p.pid));"
            "time.sleep(60)" % pidfile
        )
        rc, _ = c._push(argv=[sys.executable, "-c", code], timeout=3)
        eq(rc, br.PUSH_RC_TIMEOUT, "tree: parent timed out")
        gpid = int(open(os.path.join(root, "grandchild.pid")).read())
        dead = False
        for _ in range(50):                     # up to 5s for the group to go
            if not br.pid_alive(gpid):
                dead = True
                break
            time.sleep(0.1)
        check(dead, "tree: the grandchild was killed too, not orphaned")


def test_a_leftover_push_pid_is_swept_before_the_next_push():
    """Requirement (c), scoped to pids we spawned -- never `taskkill /IM git.exe`.

    taskkill's /FI filters have no working-directory or command-line predicate,
    so an image-name kill cannot be narrowed to this repo and would reach the
    hand lanes' git in C:\\banyan-farm\\banyan-city.
    """
    with TempRoot() as root:
        c = RecordingCourier(root)
        killed = []
        real = br._kill_process_tree
        br._kill_process_tree = lambda pid, log=print: killed.append(pid)
        try:
            c._push_pids.add(999999)
            c._push(argv=[sys.executable, "-c", "pass"], timeout=20)
        finally:
            br._kill_process_tree = real
        eq(killed, [999999], "sweep: the stale pid was killed before pushing")
        eq(c._push_pids, set(), "sweep: a clean push leaves no tracked pid")


# -- misc -------------------------------------------------------------------

def test_write_json_is_atomic_and_leaves_no_tmp():
    with TempRoot() as root:
        p = os.path.join(root, "x.json")
        br.write_json(p, {"a": 1})
        eq(json.load(open(p)), {"a": 1}, "write_json: round trip")
        check(not os.path.exists(p + ".tmp"), "write_json: no tmp left behind")


def test_tail_text_never_raises():
    check("unreadable" in br.tail_text("/definitely/not/here.log"), "tail: missing file handled")


def test_failed_count_is_visible_without_watching_for_the_event():
    """A corpse in failed/ must be countable from current state alone.

    The FAIL heartbeat fires once and is gone; this is the standing number that
    a tick sampling the queue can actually see.
    """
    with TempRoot() as root:
        q = br.Queue(root)
        eq(q.failed_count(), 0, "failed_count: empty queue reads 0")
        br.write_json(os.path.join(root, "failed", "j-dead.json"), {"id": "j-dead"})
        open(os.path.join(root, "failed", "j-dead.log"), "w").write("boom")
        eq(q.failed_count(), 1, "failed_count: one corpse, log not double-counted")
        br.write_json(os.path.join(root, "failed", "j-dead2.json"), {"id": "j-dead2"})
        eq(q.failed_count(), 2, "failed_count: counts each failed job")
        shutil.rmtree(os.path.join(root, "failed"))
        # NOT 0. It was 0, and 0 is the healthy number -- so the guard that exists
        # to make a corpse visible to a sampler reported "clean queue" whenever
        # its own count failed. Queue.__init__ creates failed/, so a missing one
        # means something removed it, which is a fact worth seeing. Still never
        # raises, which was the other half of this assertion's job.
        eq(q.failed_count(), -1, "failed_count: uncountable dir never raises, and "
                                 "never reports a healthy zero")


def test_recurring_heartbeats_carry_the_failed_count():
    """Idle and waiting-for-GPU are the lines a sampler sees; both must say it.

    And the token must not read as a job failure to farm_worker's parser, which
    keys on an uppercase `FAIL task=<id>`.
    """
    seen = []

    class FakeCourier(br.Courier):
        def __init__(self):
            br.Courier.__init__(self, "/nope", "b", "/nope")

        def mark(self, line, message, files=None, push=True):
            seen.append(line)

    c = FakeCourier()
    c.emit({"event": "runner_idle", "ready": 0, "failed": 2})
    c.emit({"event": "runner_waiting_for_gpu", "reason": "busy", "failed": 1})
    check("failed=2" in seen[0], "idle line carries the failed count")
    check("failed=1" in seen[1], "waiting line carries the failed count")
    _done, attempts = br_farm_attempts("\n".join(seen))
    eq(attempts, {}, "failed=N is not parsed as a FAIL task= mark")


def br_farm_attempts(text):
    """farm_worker's parser, imported lazily so this file stays standalone."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import farm_worker  # noqa: E402
    return farm_worker.heartbeat_attempts(text)


def test_the_sidecar_travels_with_the_clip():
    """A render's provenance record is an artifact, whether the spec says so or not.

    THE REAL ONE (2026-08-10). ltx_i2v writes `<clip>.mp4.meta.yaml` beside every
    clip it exports, and the job specs name only the mp4 -- 116 of the 117 in
    pipeline/jobs/. So "collect the artifacts" collected the clip alone, five LTX
    clips reached the tree carrying no provenance, and they were force-added.
    build_site.publishable() read the silence as permission and would have put
    them on banyan.city. Both ends are fixed; this is the end that stops the
    record being left behind at all.
    """
    with TempRoot() as root:
        clip = os.path.join(root, "07-beat.mp4")
        side = clip + ".meta.yaml"
        enqueue(root, job("j-side", [
            py_step("render", "open(%r,'w').write('mp4'); open(%r,'w').write('model: x')"
                    % (clip, side)),
        ], artifacts=[clip]))
        drain(root)
        with open(os.path.join(root, "done", "j-side.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        check(side in rec["artifacts_present"],
              "sidecar: the record beside the clip is collected with it")
        eq(rec["unprovenanced"], [], "sidecar: nothing reported missing")

    # the stem-named convention (render_t3, intake_take) counts as much
    with TempRoot() as root:
        clip = os.path.join(root, "08-beat.mp4")
        side = os.path.join(root, "08-beat.meta.yaml")
        enqueue(root, job("j-stem", [
            py_step("render", "open(%r,'w').write('mp4'); open(%r,'w').write('model: x')"
                    % (clip, side)),
        ], artifacts=[clip]))
        drain(root)
        with open(os.path.join(root, "done", "j-stem.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        check(side in rec["artifacts_present"], "sidecar: stem-named record also travels")

    # and the case that started it: a clip with no record at all
    with TempRoot() as root:
        clip = os.path.join(root, "09-beat.mp4")
        enqueue(root, job("j-bare", [
            py_step("render", "open(%r,'w').write('mp4')" % clip),
        ], artifacts=[clip]))
        drain(root)
        with open(os.path.join(root, "done", "j-bare.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        eq(rec["rc"], 0, "sidecar: a finished render is not failed over a missing yaml")
        eq(rec["unprovenanced"], [clip], "sidecar: the absence is recorded, by name")
        beat = [b for b in beats(root) if b["event"] == "job_done"][0]
        eq(beat["unprovenanced"], [clip],
           "sidecar: and it leaves the box on the heartbeat, not only in the log")
        with open(os.path.join(root, "done", "j-bare.log"), encoding="utf-8") as fh:
            log = fh.read()
        check("NO PROVENANCE RECORD" in log, "sidecar: the log says so out loud")


def test_the_done_heartbeat_names_a_clip_that_arrived_with_no_record():
    """Off-box visibility: a lane reading the branch must see it without the log."""
    seen = []

    class FakeCourier(br.Courier):
        def __init__(self):
            pass

        def mark(self, line, message, files=None, push=True):
            seen.append(line)

    c = FakeCourier()
    c.emit({"event": "job_done", "job": "j1", "artifacts": ["a.mp4"],
            "unprovenanced": [r"C:\banyan-farm\v34-r2\07-beat.mp4"]})
    c.emit({"event": "job_done", "job": "j2", "artifacts": ["a.mp4", "a.mp4.meta.yaml"]})
    check("NO-SIDECAR=1" in seen[0] and "07-beat.mp4" in seen[0],
          "heartbeat: names the clip that has no record")
    check("NO-SIDECAR" not in seen[1], "heartbeat: silent when every clip has one")
    _done, attempts = br_farm_attempts("\n".join(seen))
    eq(attempts, {}, "heartbeat: the note is not parsed as another task's mark")


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
