#!/usr/bin/env python3
"""Queue v2: the maildir directory queue plus the four §3.2 deltas.

    python3 pipeline/queue2/queue2.py enqueue <spec>.yaml [--backlog] [--again]
    python3 pipeline/queue2/queue2.py work                # claim + run ONE job
    python3 pipeline/queue2/queue2.py list
    python3 pipeline/queue2/queue2.py sweep               # startup_sweep + compaction
    python3 pipeline/queue2/queue2.py verdict <recipe_fp> <sample_job_id> <verdict> --by <who>

THE SHAPE IS v1's, ON PURPOSE. backlog/ ready/ running/ done/ failed/, filed
by write-into-staging + fsync + atomic same-volume rename, claimed by rename
out of ready/ -- the 25-year maildir/dirq pattern box_runner already drains.
Windows caveat honored (design §3.2): NTFS rename is atomic but there is no
directory fsync, so after power loss the JOURNAL is the history and the
directories are only the queue; startup_sweep reconciles the two.

WHAT v2 ADDS, each a founder-passed claim:

  1. Write-ahead journal: claim() commits a STARTED row (WAL,
     synchronous=FULL) before anything runs -- see journal.py.
  2. Idempotent enqueue: spec_fingerprint (sha256 of normalized content) is
     refused when seen in done/ + failed/ + live dirs + the journal. A spec
     is a duplicate by CONTENT, not by name (v1 guard 8's lesson: 264s of
     GPU on 2026-08-19 re-answering an answered question). --again is the
     loud override and mints a new id so it cannot overwrite the record of
     the run it is overriding.
  3. Machine residency: the queue root is a parameter, machine-local by
     default (~/banyan-queue2), and REFUSED inside the repo tree -- git as
     distributed state is the ~10-incident class §2.1 closes. One worker
     owns one root.
  4. Done means verified: complete() re-reads the output's bytes, records
     the sha256 by readback, and derives the output path from the SAME
     function the runner handed the job ({out} = output_path_for(...)) --
     no hand-typed filename can attest. No readback, no done/ row.
  5. No hand-run steps: the sweep is queue2_sweep in sweep.py, a named
     callable entrypoint for a named scheduler.
  6. Media out of git: outputs land in a content-addressed store
     (parameter, default ~/banyan-store, refused inside the repo); only
     small text records (done/ manifests, journal exports) may be
     committed.
  7. sample_before_batch: a recipe fingerprint (recipe-defining fields
     only; seed and beat excluded) is blocked from any batch -- a spec
     fanning >1, or a second job sharing the fingerprint -- until
     ledger/sample-verdicts.yaml carries a founder-verdict row for it.
     "A metric agreeing with me is not a sample" is now a return code.

HONEST EXIT CODES (the CLI maps refusals 1:1, nothing is swallowed):

    0 ok        2 bad spec/usage    3 duplicate content     4 sample-before-batch
    5 verify failed   6 journal corrupt   7 zombie/stale attempt token
    8 residency (root/store inside the repo)   9 HOLD is set   10 job step failed

Steps may declare `expected_rc: [..]` (default [0]); `allow_fail` is not in
the vocabulary -- anything outside the declared set is FAIL. Every job gets a
max_runtime kill (default 3600s), the hole box_runner is named as having.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time

try:
    from .journal import Journal, JournalCorrupt, ZombieAttempt, utcnow
except ImportError:  # run as a script: python3 pipeline/queue2/queue2.py
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from queue2.journal import Journal, JournalCorrupt, ZombieAttempt, utcnow

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ROOT = os.environ.get("BANYAN_QUEUE2_ROOT") or os.path.expanduser("~/banyan-queue2")
DEFAULT_STORE = os.environ.get("BANYAN_STORE") or os.path.expanduser("~/banyan-store")
DEFAULT_VERDICTS = os.path.join(REPO, "ledger", "sample-verdicts.yaml")

DIRS = ("incoming", "backlog", "ready", "running", "done", "failed", "control")
MAX_ATTEMPTS_DEFAULT = 2          # dead-letter after N attempts, design §2.3
MAX_RUNTIME_DEFAULT = 3600.0      # seconds; the kill box_runner lacks today

# Keys that do not define the work -- planning metadata and identity stamps.
# Two specs differing only here are the SAME work; re-filing one is the
# duplicate class, not a revision.
NONCONTENT_KEYS = ("id", "priority", "stamp_id", "filed_at", "note", "why",
                   "consumer", "success", "gate", "expires_h", "max_attempts",
                   "max_runtime")

# On top of NONCONTENT_KEYS, the recipe fingerprint also excludes what varies
# WITHIN a recipe (design §2.4: "seed and beat excluded"): two beats rendered
# with one recipe are one recipe, which is exactly what makes them a batch.
NON_RECIPE_KEYS = NONCONTENT_KEYS + ("seed", "beat", "fanout", "count",
                                     "task", "artifacts", "out_ext")

APPROVE_VERDICTS = ("pass", "approve", "approved", "go", "ship", "yes")


class Queue2Error(Exception):
    rc = 1


class SpecInvalid(Queue2Error):
    rc = 2


class DuplicateSpec(Queue2Error):
    rc = 3


class SampleBeforeBatch(Queue2Error):
    rc = 4


class VerifyFailed(Queue2Error):
    rc = 5


class ResidencyError(Queue2Error):
    rc = 8


class HoldActive(Queue2Error):
    rc = 9


# --------------------------------------------------------------------------
# Fingerprints. Deterministic: canonical JSON (sorted keys, no whitespace),
# so dict order, yaml formatting and comments can never mint a "new" spec.

def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, default=str).encode("utf-8")


def spec_fingerprint(spec: dict) -> str:
    """sha256 of the normalized spec CONTENT -- the idempotency key.

    Identity stamps and planning metadata are stripped; everything that
    changes what runs (steps, payload, env, seed, beat, recipe) is in. Same
    content under a fresh id is a duplicate; a changed spec is a revision
    and passes."""
    body = {k: v for k, v in spec.items() if k not in NONCONTENT_KEYS}
    return hashlib.sha256(_canonical(body)).hexdigest()


def recipe_fingerprint(spec: dict) -> str:
    """Hash of the recipe-DEFINING fields, distinct from the job fingerprint.

    A spec may carry an explicit `recipe:` block (model, LoRA set,
    sampler/steps/CFG, prompt template, post chain) -- that block IS the
    recipe then. Without one, the recipe is everything content-bearing minus
    what varies within a recipe (seed, beat, fanout). Either way: one
    recipe, many seeds/beats -- and many of anything is a batch."""
    block = spec.get("recipe")
    if isinstance(block, dict):
        basis = {k: v for k, v in block.items() if k not in ("seed", "beat")}
    else:
        basis = {k: v for k, v in spec.items() if k not in NON_RECIPE_KEYS}
    return hashlib.sha256(_canonical(basis)).hexdigest()


def output_path_for(store: str, job_id: str, attempt_n: int,
                    ext: str = ".bin") -> str:
    """THE one derivation of a job's output filename.

    The runner substitutes this into the step's {out}; the verifier
    recomputes it to know where to read back. One function, both callers --
    a hand-typed filename check (the rc=0-marked-FAIL incident class) has
    nowhere to live."""
    if ext and not ext.startswith("."):
        ext = "." + ext
    return os.path.join(store, "work", job_id, "attempt-%02d%s"
                        % (int(attempt_n), ext))


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# sample-verdicts ledger. Small text, repo-committable; rows are written at
# screening, when the founder looks at the one sample. Recording a verdict is
# a human-driven act -- the helper exists so the row's shape is code, not
# hand-typed yaml.

def load_sample_verdicts(path: str) -> list:
    if not os.path.exists(path):
        return []
    import yaml
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if isinstance(data, list):
        return data
    return data.get("verdicts") or []


def sample_verdict_for(path: str, recipe_fp: str):
    for row in load_sample_verdicts(path):
        if isinstance(row, dict) and row.get("fingerprint") == recipe_fp:
            return row
    return None


def record_sample_verdict(path: str, recipe_fp: str, sample_job_id: str,
                          verdict: str, by: str) -> dict:
    """Append a founder-verdict row {fingerprint, sample_job_id, verdict,
    by, date} -- the §2.4 shape -- atomically (tmp + replace)."""
    import yaml
    rows = load_sample_verdicts(path)
    row = {"fingerprint": recipe_fp, "sample_job_id": sample_job_id,
           "verdict": verdict, "by": by,
           "date": time.strftime("%Y-%m-%d", time.gmtime())}
    rows.append(row)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".",
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            yaml.safe_dump({"verdicts": rows}, fh, sort_keys=False,
                           allow_unicode=True)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return row


# --------------------------------------------------------------------------

def load_spec(path: str) -> dict:
    """Read a job spec. yaml if pyyaml is here, json otherwise."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if path.endswith(".json"):
        return json.loads(text)
    import yaml
    return yaml.safe_load(text)


class Queue2:
    def __init__(self, root: str = None, store: str = None,
                 verdicts_path: str = None, machine: str = None):
        self.root = os.path.abspath(root or DEFAULT_ROOT)
        self.store = os.path.abspath(store or DEFAULT_STORE)
        self.verdicts_path = verdicts_path or DEFAULT_VERDICTS
        self.machine = machine or platform.node()
        # Residency guard: the queue and the store are MACHINE state. Inside
        # the repo they become git state, and git-as-distributed-state is the
        # ~10-incident class this design retires (§2.1). Refused, not warned.
        for what, path in (("queue root", self.root), ("store", self.store)):
            probe = os.path.realpath(path)
            if probe == os.path.realpath(REPO) or \
                    probe.startswith(os.path.realpath(REPO) + os.sep):
                raise ResidencyError(
                    "!! %s %s is inside the repo tree %s -- media and queue "
                    "state live machine-local, never in git" % (what, path, REPO))
        for name in DIRS:
            os.makedirs(os.path.join(self.root, name), exist_ok=True)
        os.makedirs(os.path.join(self.store, "work"), exist_ok=True)
        os.makedirs(os.path.join(self.store, "objects"), exist_ok=True)
        self.journal = Journal(os.path.join(self.root, "journal.db"))

    # ---- paths and small helpers --------------------------------------

    def dir(self, name: str) -> str:
        return os.path.join(self.root, name)

    def _jobs_in(self, sub: str) -> list:
        d = self.dir(sub)
        out = []
        for name in sorted(os.listdir(d)):
            if not name.endswith(".json"):
                continue  # .HOLD-* parks and sidecars are not queue entries
            try:
                with open(os.path.join(d, name), encoding="utf-8") as fh:
                    out.append((sub, name, json.load(fh)))
            except (json.JSONDecodeError, OSError):
                # A half-readable file is a fact to report, never a crash
                # that hides the rest of the queue.
                out.append((sub, name, None))
        return out

    def _atomic_write(self, sub: str, name: str, obj: dict) -> str:
        """maildir discipline: write into incoming/ (same volume), fsync,
        rename into place as the last step. A claim can never see half a
        file."""
        fd, tmp = tempfile.mkstemp(dir=self.dir("incoming"), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        dst = os.path.join(self.dir(sub), name)
        os.replace(tmp, dst)
        return dst

    def hold_active(self):
        for name in ("HOLD",):
            p = os.path.join(self.dir("control"), name)
            if os.path.exists(p):
                return p
        return None

    # ---- claim 2: idempotent enqueue -----------------------------------

    def seen_fingerprints(self) -> dict:
        """spec_fp -> where, across live AND terminal states AND the journal.
        v1's guards compared against live work only; that is how a finished
        job owned nothing and a re-file walked straight in."""
        seen = {}
        for sub in ("backlog", "ready", "running", "done", "failed"):
            for _, name, job in self._jobs_in(sub):
                if job and job.get("spec_fp"):
                    seen.setdefault(job["spec_fp"], "%s/%s" % (sub, name))
        return seen

    def _recipe_jobs_on_disk(self, recipe_fp: str,
                             exclude_spec_fp: str = "") -> int:
        """Distinct spec contents per recipe, widest fanout each -- an
        identical re-file is the same sample again, not a wider batch."""
        widest = {}
        for sub in ("backlog", "ready", "running", "done", "failed"):
            for _, _, job in self._jobs_in(sub):
                if not job or job.get("recipe_fp") != recipe_fp:
                    continue
                fp = job.get("spec_fp")
                if fp == exclude_spec_fp:
                    continue
                widest[fp] = max(widest.get(fp, 0), int(job.get("fanout", 1)))
        return sum(widest.values())

    def enqueue(self, spec: dict, backlog: bool = False,
                again: bool = False) -> dict:
        hold = self.hold_active()
        if hold:
            raise HoldActive("!! %s is set -- the queue refuses new work "
                             "until the founder unholds" % hold)
        jid = spec.get("id")
        if not jid:
            raise SpecInvalid("!! spec has no id")
        steps = spec.get("steps") or []
        if not steps:
            raise SpecInvalid("!! spec %s has no steps" % jid)
        for i, step in enumerate(steps):
            if not step.get("argv"):
                raise SpecInvalid("!! spec %s step %d has no argv" % (jid, i))

        spec_fp = spec_fingerprint(spec)
        recipe_fp = recipe_fingerprint(spec)
        fanout = int(spec.get("fanout", spec.get("count", 1)))

        if not again:
            seen = self.seen_fingerprints()
            where = seen.get(spec_fp)
            if where is None and self.journal.spec_fp_known(spec_fp):
                where = "journal"
            if where:
                raise DuplicateSpec(
                    "!! spec %s is byte-equivalent to work already owned by "
                    "%s (spec_fp %s) -- a duplicate by content, not by name; "
                    "--again is the loud override" % (jid, where, spec_fp[:12]))

        # claim 7: sample_before_batch. One job with a new recipe IS the
        # sample; anything that makes the recipe's population exceed one --
        # this spec fanning wider, or a sibling already filed/run -- needs
        # the founder's verdict row first.
        already = max(self.journal.recipe_count(recipe_fp, spec_fp),
                      self._recipe_jobs_on_disk(recipe_fp, spec_fp))
        if fanout > 1 or already >= 1:
            row = sample_verdict_for(self.verdicts_path, recipe_fp)
            if row is None:
                raise SampleBeforeBatch(
                    "!! recipe %s would total %d jobs but "
                    "ledger/sample-verdicts.yaml has no founder-verdict row "
                    "for it -- render ONE, screen it, record the verdict "
                    "(queue2.py verdict), then batch. A metric agreeing with "
                    "the steward is not a sample."
                    % (recipe_fp[:12], already + fanout))
            if str(row.get("verdict", "")).lower() not in APPROVE_VERDICTS:
                raise SampleBeforeBatch(
                    "!! recipe %s has a founder verdict and it is %r (by %s, "
                    "%s) -- a rejected sample does not batch"
                    % (recipe_fp[:12], row.get("verdict"), row.get("by"),
                       row.get("date")))

        # id stamping, v1 convention: epoch-suffix unless opted out, so a
        # re-filed name never inherits its predecessor's spent attempts.
        if spec.get("stamp_id", True) and not jid[-10:].isdigit():
            jid = "%s-%d" % (jid, int(time.time()))
        if again:
            jid = "%s-again%06x" % (jid, time.time_ns() % 0x1000000)

        job = {
            "id": jid,
            "task": spec.get("task", spec.get("id")),
            "node": spec.get("node"),
            "beat": spec.get("beat"),
            "worker": "queue2",
            "priority": spec.get("priority", 100),
            "needs_gpu": bool(spec.get("needs_gpu", True)),
            "max_attempts": int(spec.get("max_attempts", MAX_ATTEMPTS_DEFAULT)),
            "max_runtime": float(spec.get("max_runtime", MAX_RUNTIME_DEFAULT)),
            "env": spec.get("env") or {},
            "steps": steps,
            "out_ext": spec.get("out_ext", ".bin"),
            "fanout": fanout,
            "spec_fp": spec_fp,
            "recipe_fp": recipe_fp,
            "filed_at": utcnow(),
        }
        # Journal first (write-ahead applies to filing too), then the file.
        self.journal.record_enqueued(jid, spec_fp, recipe_fp, fanout)
        path = self._atomic_write("backlog" if backlog else "ready",
                                  jid + ".json", job)
        return {"id": jid, "path": path, "spec_fp": spec_fp,
                "recipe_fp": recipe_fp}

    # ---- claims 1 and 4: claim / complete / fail ------------------------

    def claim(self, pid: int = None):
        """Oldest ready job -> running/, write-ahead. The STARTED row is
        committed at synchronous=FULL BEFORE the rename and before any work,
        so the attempt exists in history even if the machine bluescreens one
        second later. Returns (job, attempt_token, attempt_n) or None."""
        for _, name, job in self._jobs_in("ready"):
            if job is None:
                continue
            src = os.path.join(self.dir("ready"), name)
            spent = self.journal.attempt_count(job["id"])
            cap = int(job.get("max_attempts", MAX_ATTEMPTS_DEFAULT))
            if spent >= cap:
                # A re-filed id inheriting spent attempts (v1 problem 2)
                # retires here, visibly, instead of looping.
                job["fail_reason"] = ("attempts exhausted before claim: "
                                      "%d of %d" % (spent, cap))
                self._atomic_write("failed", name, job)
                os.unlink(src)
                continue
            token = self.journal.record_started(
                job["id"], spent + 1, self.machine, pid or os.getpid())
            try:
                os.rename(src, os.path.join(self.dir("running"), name))
            except OSError as exc:
                # One worker per root by design; a race here means that
                # invariant broke. The attempt is spent -- honestly.
                self.journal.record_failed(token, "claim raced: %s" % exc)
                continue
            return job, token, spent + 1
        return None

    def complete(self, job: dict, token: int, attempt_n: int) -> dict:
        """VERIFY-THEN-ATTEST. No done/ record until the output's bytes have
        been RE-READ and their sha256 recorded -- sha of content is the only
        existence proof; size, name and manifest presence prove nothing (the
        88-93%-holes weights are the type specimen). The path is derived by
        output_path_for -- the same function that handed the job its {out}."""
        out = output_path_for(self.store, job["id"], attempt_n,
                              job.get("out_ext", ".bin"))
        if not os.path.exists(out):
            raise VerifyFailed("!! job %s attempt %d: derived output %s does "
                               "not exist -- nothing to attest, nothing done"
                               % (job["id"], attempt_n, out))
        nbytes = os.path.getsize(out)
        if nbytes == 0:
            raise VerifyFailed("!! job %s attempt %d: output %s is 0 bytes -- "
                               "an empty artifact is a failure with a "
                               "filename" % (job["id"], attempt_n, out))
        sha = file_sha256(out)  # the readback

        # Journal DONE first (zombie-guarded: a swept attempt cannot attest),
        # then move bytes into the content-addressed store, then the done/
        # manifest. If we crash mid-sequence the journal already holds the
        # truth and sweep reconciles the directories to it.
        store_path = os.path.join(
            self.store, "objects", sha[:2],
            sha + os.path.splitext(out)[1])
        self.journal.attest_done(token, store_path, sha, nbytes)
        os.makedirs(os.path.dirname(store_path), exist_ok=True)
        if not os.path.exists(store_path):
            os.replace(out, store_path)
        else:
            os.unlink(out)  # content-addressed: same bytes already stored

        name = job["id"] + ".json"
        job = dict(job)
        job.update({"attempt_n": attempt_n, "readback_sha256": sha,
                    "readback_bytes": nbytes, "readback_ts": utcnow(),
                    "store_path": store_path})
        self._atomic_write("done", name, job)
        running = os.path.join(self.dir("running"), name)
        if os.path.exists(running):
            os.unlink(running)
        return job

    def fail(self, job: dict, token: int, reason: str) -> str:
        """Journal the failure, then requeue or dead-letter. After
        max_attempts (default 2) the job retires to failed/ with its reason
        -- a first-class dead-letter, not a loop."""
        self.journal.record_failed(token, reason)
        name = job["id"] + ".json"
        running = os.path.join(self.dir("running"), name)
        spent = self.journal.attempt_count(job["id"])
        cap = int(job.get("max_attempts", MAX_ATTEMPTS_DEFAULT))
        if spent >= cap:
            job = dict(job)
            job["fail_reason"] = reason
            job["attempts"] = spent
            self._atomic_write("failed", name, job)
            if os.path.exists(running):
                os.unlink(running)
            return "failed"
        os.rename(running, os.path.join(self.dir("ready"), name))
        return "requeued"

    # ---- the worker's one-job runner ------------------------------------

    def run_job(self, job: dict, token: int, attempt_n: int) -> int:
        """Run one claimed job's steps and verify-then-attest the output.

        Honest exit codes throughout: a step's rc must be in its declared
        expected_rc set (default [0]) -- `allow_fail` is not in the
        vocabulary. Every job runs under a max_runtime kill. Returns 0 on
        attested DONE, else the class rc of what refused."""
        out = output_path_for(self.store, job["id"], attempt_n,
                              job.get("out_ext", ".bin"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        env = dict(os.environ)
        env.update({str(k): str(v) for k, v in (job.get("env") or {}).items()})
        deadline = time.monotonic() + float(job.get("max_runtime",
                                                    MAX_RUNTIME_DEFAULT))
        for i, step in enumerate(job.get("steps") or []):
            argv = [str(a).replace("{out}", out).replace("{store}", self.store)
                    for a in step["argv"]]
            expected = [int(rc) for rc in step.get("expected_rc", [0])]
            budget = deadline - time.monotonic()
            if budget <= 0:
                self.fail(job, token, "max_runtime %.1fs exceeded before "
                          "step %d" % (job.get("max_runtime"), i))
                return 10
            try:
                # utf-8 + errors=replace on every pipe (reader_hygiene,
                # §2.3): cmd.exe answers in cp1252 and a decode error on the
                # reader thread silently becomes stdout=None.
                proc = subprocess.run(argv, capture_output=True, text=True,
                                      encoding="utf-8", errors="replace",
                                      env=env, timeout=budget)
            except subprocess.TimeoutExpired:
                self.fail(job, token, "max_runtime %.1fs exceeded in step %d "
                          "(%s) -- killed" % (job.get("max_runtime"), i,
                                              argv[0]))
                return 10
            except OSError as exc:
                self.fail(job, token, "step %d could not spawn: %s" % (i, exc))
                return 10
            if proc.returncode not in expected:
                tail = (proc.stderr or "").strip().splitlines()[-3:]
                self.fail(job, token, "step %d rc=%d not in expected %s; "
                          "stderr tail: %s" % (i, proc.returncode, expected,
                                               " | ".join(tail)))
                return 10
        try:
            self.complete(job, token, attempt_n)
        except VerifyFailed as exc:
            self.fail(job, token, str(exc))
            return VerifyFailed.rc
        return 0

    # ---- reporting -------------------------------------------------------

    def counts(self) -> dict:
        return {sub: sum(1 for _, n, _ in self._jobs_in(sub))
                for sub in ("backlog", "ready", "running", "done", "failed")}


# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=None, help="queue root (machine-local)")
    ap.add_argument("--store", default=None, help="content-addressed store")
    ap.add_argument("--verdicts", default=None,
                    help="sample-verdicts yaml (default ledger/sample-verdicts.yaml)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("enqueue")
    p.add_argument("spec")
    p.add_argument("--backlog", action="store_true")
    p.add_argument("--again", action="store_true")

    sub.add_parser("work", help="claim and run ONE job, honestly")
    sub.add_parser("list")
    sub.add_parser("sweep")

    p = sub.add_parser("verdict", help="record a founder sample verdict row")
    p.add_argument("fingerprint")
    p.add_argument("sample_job_id")
    p.add_argument("verdict")
    p.add_argument("--by", required=True)

    args = ap.parse_args(argv)
    try:
        if args.cmd == "verdict":
            row = record_sample_verdict(
                args.verdicts or DEFAULT_VERDICTS, args.fingerprint,
                args.sample_job_id, args.verdict, args.by)
            print("recorded: %s" % json.dumps(row, sort_keys=True))
            return 0
        q = Queue2(root=args.root, store=args.store,
                   verdicts_path=args.verdicts)
        if args.cmd == "enqueue":
            res = q.enqueue(load_spec(args.spec), backlog=args.backlog,
                            again=args.again)
            print("enqueued %s -> %s" % (res["id"], res["path"]))
            return 0
        if args.cmd == "list":
            for k, v in q.counts().items():
                print("%8s  %d" % (k, v))
            return 0
        if args.cmd == "work":
            got = q.claim()
            if got is None:
                print("ready/ is empty -- nothing claimed (a reportable "
                      "state, not an error)")
                return 0
            job, token, attempt_n = got
            rc = q.run_job(job, token, attempt_n)
            print("job %s attempt %d -> rc %d" % (job["id"], attempt_n, rc))
            return rc
        if args.cmd == "sweep":
            try:
                from .sweep import queue2_sweep
            except ImportError:
                from queue2.sweep import queue2_sweep
            return queue2_sweep(root=args.root, store=args.store,
                                verdicts_path=args.verdicts)
    except Queue2Error as exc:
        print(exc, file=sys.stderr)
        return exc.rc
    except (JournalCorrupt, ZombieAttempt) as exc:
        print(exc, file=sys.stderr)
        return exc.rc
    return 2


if __name__ == "__main__":
    sys.exit(main())
