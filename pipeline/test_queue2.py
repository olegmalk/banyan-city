#!/usr/bin/env python3
"""Induced-failure tests for queue v2 (pipeline/queue2/).

Pure-local: tmpdir queues, no ffmpeg, no network, no GPU, nothing touches the
repo tree (the residency test asserts exactly that refusal). Every founder-
passed claim gets its failure INDUCED, not assumed: a worker is kill -9'd
mid-job, the journal db is truncated on purpose, an output goes missing
before attest, a batch knocks before its sample verdict exists.

Run: python3 pipeline/test_queue2.py
"""

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE))

from queue2 import (
    DuplicateSpec, HoldActive, Journal, JournalCorrupt, Queue2,
    ResidencyError, SampleBeforeBatch, VerifyFailed, ZombieAttempt,
    output_path_for, queue2_sweep, recipe_fingerprint, record_sample_verdict,
    spec_fingerprint, startup_sweep,
)
from queue2.sweep import compact_journal

REPO = PIPELINE.parent
FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


def mkq(td, **kw):
    return Queue2(root=os.path.join(td, "queue"),
                  store=os.path.join(td, "store"),
                  verdicts_path=os.path.join(td, "sample-verdicts.yaml"),
                  **kw)


def spec(sid, seed=1, model="m1", argv=None, **kw):
    s = {"id": sid, "stamp_id": False, "seed": seed, "model": model,
         "needs_gpu": False,
         "steps": [{"argv": argv or ["sh", "-c", "echo payload > {out}"]}]}
    s.update(kw)
    return s


def write_output(q, job, attempt_n, data=b"rendered bytes"):
    out = output_path_for(q.store, job["id"], attempt_n,
                          job.get("out_ext", ".bin"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as fh:
        fh.write(data)
    return out


def dead_pid():
    """A pid that certainly existed and is certainly gone: our own reaped
    child. No magic numbers that might collide with a live process."""
    p = subprocess.Popen(["sleep", "0"])
    p.wait()
    return p.pid


# --------------------------------------------------------------------------

def test_fingerprints(td):
    a = spec("job-a", seed=7, model="wan2.1")
    b = spec("job-b", seed=7, model="wan2.1")      # only identity differs
    c = spec("job-c", seed=8, model="wan2.1")      # seed differs
    d = spec("job-d", seed=7, model="ltx-video")   # recipe differs
    check("same content under a fresh id is the same fingerprint",
          spec_fingerprint(a) == spec_fingerprint(b))
    check("a changed seed is a different JOB",
          spec_fingerprint(a) != spec_fingerprint(c))
    check("but the same RECIPE (seed excluded, per the design)",
          recipe_fingerprint(a) == recipe_fingerprint(c))
    check("a changed model is a different recipe",
          recipe_fingerprint(a) != recipe_fingerprint(d))
    e = dict(a, note="planning prose", priority=5, why="because")
    check("planning metadata cannot mint a new spec",
          spec_fingerprint(a) == spec_fingerprint(e))
    r1 = dict(spec("job-r"), recipe={"model": "x", "steps": 30, "seed": 9})
    r2 = dict(spec("job-r2"), recipe={"model": "x", "steps": 30, "seed": 4})
    check("an explicit recipe: block is the recipe, its seed excluded",
          recipe_fingerprint(r1) == recipe_fingerprint(r2))


def test_residency_and_atomic_enqueue(td):
    for what, kw in (("root", {"root": os.path.join(str(REPO), "nope-q2"),
                               "store": os.path.join(td, "s")}),
                     ("store", {"root": os.path.join(td, "q"),
                                "store": os.path.join(str(REPO), "nope-store")})):
        raised = False
        try:
            Queue2(verdicts_path=os.path.join(td, "v.yaml"), **kw)
        except ResidencyError:
            raised = True
        check("a %s inside the repo tree is refused" % what, raised)
    check("and refused BEFORE anything is created in the repo",
          not os.path.exists(os.path.join(str(REPO), "nope-q2"))
          and not os.path.exists(os.path.join(str(REPO), "nope-store")))

    q = mkq(td)
    res = q.enqueue(spec("first"))
    ready = os.path.join(q.dir("ready"), "first.json")
    check("enqueue lands the job in ready/", os.path.exists(ready))
    check("staging is empty after the rename (maildir discipline)",
          os.listdir(q.dir("incoming")) == [])
    job = json.load(open(ready))
    check("the filed job carries both fingerprints",
          job["spec_fp"] == res["spec_fp"]
          and job["recipe_fp"] == res["recipe_fp"])
    res2 = q.enqueue(spec("later", model="m-backlog"), backlog=True)
    check("--backlog files into backlog/, not ready/",
          "backlog" in res2["path"] and os.path.exists(res2["path"]))


def test_hold_refuses_new_work(td):
    q = mkq(td)
    open(os.path.join(q.dir("control"), "HOLD"), "w").close()
    raised = False
    try:
        q.enqueue(spec("held-out"))
    except HoldActive:
        raised = True
    check("control/HOLD refuses enqueue -- the stop is code, not prose",
          raised)


def test_duplicate_rejected_across_live_and_terminal(td):
    q = mkq(td)

    def refused(s):
        try:
            q.enqueue(s)
            return False
        except DuplicateSpec:
            return True

    q.enqueue(spec("orig", model="dup-live"))
    check("duplicate refused while the twin sits in ready/",
          refused(spec("renamed", model="dup-live")))
    job, token, n = q.claim()
    check("duplicate refused while the twin is running",
          refused(spec("renamed2", model="dup-live")))
    write_output(q, job, n)
    q.complete(job, token, n)
    check("duplicate refused against done/ -- terminal work still owns "
          "its content (the 264s-of-GPU class)",
          refused(spec("renamed3", model="dup-live")))

    q.enqueue(spec("doomed", model="dup-dead", max_attempts=2,
                   argv=["sh", "-c", "exit 1"]))
    for _ in range(2):
        j2, t2, _ = q.claim()
        q.fail(j2, t2, "induced")
    check("two failures dead-letter the job",
          os.path.exists(os.path.join(q.dir("failed"), "doomed.json")))
    check("duplicate refused against failed/ too",
          refused(spec("doomed-again", model="dup-dead", max_attempts=2,
                       argv=["sh", "-c", "exit 1"])))
    res = q.enqueue(spec("renamed4", model="dup-live"), again=True)
    check("--again is the loud override and mints a fresh id",
          res["id"].startswith("renamed4-again"))


WORKER_SRC = """\
import sys, time
sys.path.insert(0, sys.argv[4])
from queue2 import Queue2
q = Queue2(root=sys.argv[1], store=sys.argv[2], verdicts_path=sys.argv[3])
got = q.claim()
print("CLAIMED %s" % (got and got[0]["id"]), flush=True)
time.sleep(60)   # mid-job forever, until somebody kill -9s us
"""


def test_write_ahead_survives_kill9(td):
    q = mkq(td)
    q.enqueue(spec("victim", model="kill9", max_attempts=1))
    script = os.path.join(td, "worker.py")
    with open(script, "w") as fh:
        fh.write(WORKER_SRC)
    proc = subprocess.Popen(
        [sys.executable, script, q.root, q.store, q.verdicts_path,
         str(PIPELINE)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    line = proc.stdout.readline().strip()
    check("the worker subprocess claimed the job", line == "CLAIMED victim")
    os.kill(proc.pid, signal.SIGKILL)
    proc.wait()

    rows = q.journal.attempts_for("victim")
    check("the journal shows the attempt the kill could not erase "
          "(write-ahead: STARTED committed before work)",
          len(rows) == 1 and rows[0]["state"] == "STARTED"
          and rows[0]["pid"] == proc.pid)
    check("pragmas are the crash-proof pair the design names",
          q.journal.db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
          and q.journal.db.execute("PRAGMA synchronous").fetchone()[0] == 2)

    report = startup_sweep(q)
    check("sweep saw the dead pid and retired the attempt",
          report["interrupted"] == 1 and report["retired"] == 1)
    rows = q.journal.attempts_for("victim")
    check("the attempt is INTERRUPTED with a reason, budget CONSUMED",
          rows[0]["state"] == "INTERRUPTED"
          and "consumed" in (rows[0]["reason"] or ""))
    failed = os.path.join(q.dir("failed"), "victim.json")
    check("max_attempts=1 means the job dead-letters, it does not loop",
          os.path.exists(failed)
          and not os.path.exists(os.path.join(q.dir("running"), "victim.json"))
          and "gone" in json.load(open(failed))["fail_reason"])


def test_sweep_requeues_then_retires_and_zombies_cannot_attest(td):
    q = mkq(td)
    q.enqueue(spec("bsod", model="bsod", max_attempts=2))

    job, token1, n1 = q.claim(pid=dead_pid())   # BSOD-style: owner vanished
    report = startup_sweep(q)
    check("attempt 1 of 2: sweep requeues the job",
          report["requeued"] == 1
          and os.path.exists(os.path.join(q.dir("ready"), "bsod.json")))
    check("a host-killing death consumed budget anyway",
          q.journal.attempt_count("bsod") == 1)

    write_output(q, job, n1)
    raised = False
    try:
        q.complete(job, token1, n1)
    except ZombieAttempt:
        raised = True
    check("the swept attempt's token cannot attest DONE (zombie guard)",
          raised)
    check("and nothing reached done/",
          not os.path.exists(os.path.join(q.dir("done"), "bsod.json")))

    job, token2, n2 = q.claim(pid=dead_pid())
    startup_sweep(q)
    check("attempt 2 of 2: dead-letter, attempts preserved in the journal",
          os.path.exists(os.path.join(q.dir("failed"), "bsod.json"))
          and [r["state"] for r in q.journal.attempts_for("bsod")]
          == ["INTERRUPTED", "INTERRUPTED"])


def test_verify_then_attest(td):
    q = mkq(td)
    q.enqueue(spec("proof", model="attest"))
    job, token, n = q.claim()

    def cannot_complete(why):
        try:
            q.complete(job, token, n)
            return False
        except VerifyFailed:
            return not os.path.exists(os.path.join(q.dir("done"),
                                                   "proof.json"))
    check("no output at the DERIVED path -> no done/ (missing)",
          cannot_complete("missing"))
    hand_typed = os.path.join(q.store, "work", "proof", "my-output.bin")
    os.makedirs(os.path.dirname(hand_typed), exist_ok=True)
    open(hand_typed, "wb").write(b"real bytes, wrong name")
    check("a hand-typed filename cannot attest -- only output_path_for's",
          cannot_complete("hand-typed"))
    write_output(q, job, n, data=b"")
    check("a 0-byte artifact is a failure with a filename, not a done",
          cannot_complete("empty"))

    out = write_output(q, job, n, data=b"actual pixels")
    rec = q.complete(job, token, n)
    done = json.load(open(os.path.join(q.dir("done"), "proof.json")))
    import hashlib
    want = hashlib.sha256(b"actual pixels").hexdigest()
    check("done/ row carries the READBACK sha256 + ts, and it matches",
          done["readback_sha256"] == want and done["readback_ts"]
          and done["readback_bytes"] == len(b"actual pixels"))
    check("bytes moved into the content-addressed store, outside the repo",
          os.path.exists(rec["store_path"])
          and want in rec["store_path"]
          and not os.path.realpath(rec["store_path"]).startswith(
              os.path.realpath(str(REPO)) + os.sep)
          and not os.path.exists(out))
    jr = q.journal.attempts_for("proof")[-1]
    check("the journal attested the same readback",
          jr["state"] == "DONE" and jr["readback_sha256"] == want)


def test_corrupt_journal_is_loud_then_recoverable(td):
    q = mkq(td)
    q.enqueue(spec("kept", model="corrupt-test"))
    job, token, n = q.claim()
    write_output(q, job, n)
    q.complete(job, token, n)
    q.journal.close()

    db = os.path.join(q.root, "journal.db")
    size = os.path.getsize(db)
    with open(db, "r+b") as fh:
        fh.seek(512)
        fh.write(b"NOT A BTREE PAGE" * 32)   # scribble mid-file
        fh.truncate(max(700, size // 3))     # and truncate it
    raised = ""
    try:
        Journal(db)
    except JournalCorrupt as exc:
        raised = str(exc)
    check("a truncated journal raises a clean error naming the recovery "
          "path -- never a silent zero-attempt answer",
          "recover" in raised.lower())
    raised2 = False
    try:
        Queue2(root=q.root, store=q.store, verdicts_path=q.verdicts_path)
    except JournalCorrupt:
        raised2 = True
    check("the queue refuses to open over it too", raised2)

    j2, quarantine = Journal.recover(db)
    check("recovery quarantines the corpse and says so on the record",
          os.path.exists(quarantine)
          and j2.recovered_from() == quarantine)
    j2.close()
    q2 = Queue2(root=q.root, store=q.store, verdicts_path=q.verdicts_path)
    dup = False
    try:
        q2.enqueue(spec("kept-refile", model="corrupt-test"))
    except DuplicateSpec:
        dup = True
    check("after journal loss, done/ still owns its content -- dedupe "
          "does not silently reopen", dup)


def test_sample_before_batch(td):
    q = mkq(td)
    blocked = False
    try:
        q.enqueue(spec("wave", model="recipeX", fanout=2))
    except SampleBeforeBatch:
        blocked = True
    check("a 2-wide spec is blocked with no verdict row", blocked)

    res = q.enqueue(spec("the-sample", model="recipeX", seed=1))
    check("ONE job with a new recipe is the sample, and it passes",
          os.path.exists(res["path"]))
    blocked2 = False
    try:
        q.enqueue(spec("sibling", model="recipeX", seed=2))
    except SampleBeforeBatch as exc:
        blocked2 = "sample-verdicts" in str(exc)
    check("a second job on the same recipe is a batch and is blocked, "
          "naming the ledger it needs", blocked2)

    record_sample_verdict(q.verdicts_path, res["recipe_fp"],
                          res["id"], "pass", "founder")
    import yaml
    rows = yaml.safe_load(open(q.verdicts_path))["verdicts"]
    check("the verdict row has the §2.4 shape",
          rows[0]["fingerprint"] == res["recipe_fp"]
          and rows[0]["sample_job_id"] == res["id"]
          and rows[0]["verdict"] == "pass" and rows[0]["by"] == "founder"
          and rows[0]["date"])
    ok2 = q.enqueue(spec("sibling", model="recipeX", seed=2))
    ok3 = q.enqueue(spec("wave", model="recipeX", seed=3, fanout=2))
    check("the founder's verdict admits the batch",
          os.path.exists(ok2["path"]) and os.path.exists(ok3["path"]))

    neg = q.enqueue(spec("bad-sample", model="recipeY", seed=1))
    record_sample_verdict(q.verdicts_path, neg["recipe_fp"],
                          neg["id"], "kill", "founder")
    still = False
    try:
        q.enqueue(spec("bad-sibling", model="recipeY", seed=2))
    except SampleBeforeBatch as exc:
        still = "kill" in str(exc)
    check("a REJECTED sample does not batch either", still)


def test_run_job_honest_exit_codes(td):
    q = mkq(td)

    q.enqueue(spec("clean", model="rc-ok"))
    job, token, n = q.claim()
    check("a clean run attests and returns 0",
          q.run_job(job, token, n) == 0
          and os.path.exists(os.path.join(q.dir("done"), "clean.json")))

    q.enqueue(spec("liar", model="rc-liar", argv=["sh", "-c", "exit 3"]))
    job, token, n = q.claim()
    rc = q.run_job(job, token, n)
    reason = q.journal.attempts_for("liar")[-1]["reason"] or ""
    check("rc=3 against expected [0] FAILS loudly -- no allow_fail",
          rc == 10 and "rc=3" in reason
          and os.path.exists(os.path.join(q.dir("ready"), "liar.json")))

    declared = spec("declared", model="rc-declared")
    declared["steps"] = [{"argv": ["sh", "-c", "echo hi > {out}; exit 3"],
                          "expected_rc": [3]}]
    q.enqueue(declared)
    # ready/ also holds the requeued "liar"; drain claims until ours.
    job, token, n = q.claim()
    if job["id"] != "declared":
        q.fail(job, token, "test drain")
        job, token, n = q.claim()
    check("a DECLARED expected_rc set passes -- honest, not permissive",
          job["id"] == "declared" and q.run_job(job, token, n) == 0)

    q.enqueue(spec("stuck", model="rc-stuck", max_runtime=0.6,
                   max_attempts=1, argv=["sleep", "30"]))
    job, token, n = q.claim()
    while job["id"] != "stuck":
        q.fail(job, token, "test drain")
        job, token, n = q.claim()
    t0 = time.time()
    rc = q.run_job(job, token, n)
    reason = q.journal.attempts_for("stuck")[-1]["reason"] or ""
    check("max_runtime kills the job and says so",
          rc == 10 and "max_runtime" in reason and time.time() - t0 < 10
          and os.path.exists(os.path.join(q.dir("failed"), "stuck.json")))


def test_sweep_entrypoint_and_compaction(td):
    q = mkq(td)
    q.enqueue(spec("compactable", model="sweep-test"))
    job, token, n = q.claim()
    write_output(q, job, n)
    q.complete(job, token, n)

    rc = queue2_sweep(q=q, keep_days=0.0)
    check("queue2_sweep is a callable entrypoint and exits 0", rc == 0)
    exports = [f for f in os.listdir(q.dir("control"))
               if f.startswith("journal-export-")]
    check("compaction exported the terminal rows BEFORE deleting them "
          "(small text record, the committable class)",
          len(exports) == 1)
    lines = open(os.path.join(q.dir("control"), exports[0])).read().splitlines()
    check("the export holds the attempt, sha and all",
          len(lines) == 1
          and json.loads(lines[0])["job_id"] == "compactable"
          and json.loads(lines[0])["readback_sha256"])
    check("the jobs table survives compaction -- idempotency memory is "
          "never compacted away",
          q.journal.spec_fp_known(job["spec_fp"]))


# --------------------------------------------------------------------------

def main():
    tests = [
        test_fingerprints,
        test_residency_and_atomic_enqueue,
        test_hold_refuses_new_work,
        test_duplicate_rejected_across_live_and_terminal,
        test_write_ahead_survives_kill9,
        test_sweep_requeues_then_retires_and_zombies_cannot_attest,
        test_verify_then_attest,
        test_corrupt_journal_is_loud_then_recoverable,
        test_sample_before_batch,
        test_run_job_honest_exit_codes,
        test_sweep_entrypoint_and_compaction,
    ]
    for t in tests:
        print("-- " + t.__name__)
        with tempfile.TemporaryDirectory() as td:
            t(td)
    print()
    if FAILURES:
        print("FAILED %d:" % len(FAILURES))
        for f in FAILURES:
            print("  - " + f)
        return 1
    print("all queue2 checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
