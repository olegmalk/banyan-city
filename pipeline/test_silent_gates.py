#!/usr/bin/env python3
"""Tests for the guards that stop a check reporting health while it is dead.

The regressions here all have one shape, found four times in one day on
2026-08-10 and each time by accident, hours late: a check whose answer is green
when the thing it reads is broken. A failed job that was an event and never a
state; a page that was never copied and so was invisible to every gate; a
freshness check reading a clock that could not move; a 403 swallowed into a
green workflow.

The question each test below asks is the one that separates a check from a
decoration: WHAT WOULD THIS PRINT IF THE THING IT READS WERE COMPLETELY BROKEN?
If the answer is "the same as when everything is fine", the check is scenery.

These live in their own file rather than in test_pipeline.py so the guards keep
one obvious home as more of them are found.

Run: python3 pipeline/test_silent_gates.py
"""

import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

FAILURES = []
PASSED = 0


def check(name, cond):
    global PASSED
    print(("  ok  " if cond else "FAIL  ") + name)
    if cond:
        PASSED += 1
    else:
        FAILURES.append(name)


# ---------------------------------------------------------------- check_sync

NODE_MD = """\
# a node

## Script

**FIRST BEAT — 0:00–0:04**

> **VOICE:** hello there

**SECOND BEAT — 0:04–0:08**

> **VOICE:** and again
"""

SHOTS_MD = """\
# shots

## Beat 01 — FIRST BEAT (0:00-0:04)

a note about the shot

```
first beat prompt
```

## Beat 02 — SECOND BEAT (0:04-0:08)

another note

```
second beat prompt
```
"""


def node_at(root: Path, node_md: str, shots_md: str) -> None:
    d = root / "genomes" / "sapling" / "nodes" / "001-a-node"
    d.mkdir(parents=True)
    (d / "node.md").write_text(node_md, encoding="utf-8")
    (d / "shots.md").write_text(shots_md, encoding="utf-8")


def test_check_sync_cannot_pass_on_a_script_it_could_not_read():
    """Zero parsed beats used to print "agree on every beat" and exit 0.

    Every check in check_sync is a loop over the parsed beats, and the verdict is
    "no findings" — so a node.md with no `## Script` heading, or a beat-heading
    style that drifts from what parse_script matches, ran every loop zero times
    and produced the tick. With BOTH files unparseable it is quieter still: the
    one structural check is `len(script) != len(shots)`, and 0 != 0 is false.

    That tick is not idle: check_sync is a render gate (render_local.py) and its
    sentence is quoted verbatim in the review READMEs the founder reads.
    """
    import check_sync as cs

    real_repo = cs.REPO
    try:
        with tempfile.TemporaryDirectory() as td:
            cs.REPO = Path(td)
            node_at(Path(td), NODE_MD, SHOTS_MD)
            check("sync: a readable node still passes clean",
                  cs.check("sapling", "001") == [])

        with tempfile.TemporaryDirectory() as td:
            cs.REPO = Path(td)
            node_at(Path(td), "# a node\n\nno script section at all\n", SHOTS_MD)
            found = cs.check("sapling", "001")
            check("sync: an unparseable node.md is a FAIL, not a tick",
                  any(f["what"] == "unreadable script" and f["sev"] == "FAIL"
                      for f in found))

        with tempfile.TemporaryDirectory() as td:
            cs.REPO = Path(td)
            node_at(Path(td), NODE_MD, "# shots\n\nnothing beat-shaped here\n")
            found = cs.check("sapling", "001")
            check("sync: an unparseable shots.md is a FAIL, not a tick",
                  any(f["what"] == "unreadable shots" and f["sev"] == "FAIL"
                      for f in found))

        with tempfile.TemporaryDirectory() as td:
            cs.REPO = Path(td)
            node_at(Path(td), "# nothing\n", "# nothing\n")
            found = cs.check("sapling", "001")
            # the case the old code was completely silent on: 0 == 0
            check("sync: both files unreadable is two FAILs, not agreement",
                  len([f for f in found if f["sev"] == "FAIL"]) >= 2)
    finally:
        cs.REPO = real_repo


# --------------------------------------------------------------- farm_worker

class FakeRun:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def queue_head_with(fetch_rc, show):
    """Run farm_worker.queue_head() against canned git results. (tasks, output)."""
    import farm_worker as fw

    real_sh = fw.sh
    buf = io.StringIO()
    try:
        def fake_sh(*args, **kw):
            return FakeRun(fetch_rc) if args[1] == "fetch" else show
        fw.sh = fake_sh
        with redirect_stdout(buf):
            tasks = fw.queue_head()
    finally:
        fw.sh = real_sh
    return tasks, buf.getvalue()


def test_a_queue_the_worker_cannot_read_is_never_reported_as_empty():
    """"I can't see the queue" and "the queue is empty" are opposite facts.

    queue_head's docstring is a monument to that distinction — it was learned
    when a failed fetch idled the 5090 for hours beside five queued jobs — and
    the branch between the two it already handled, a nonzero `git show`, was
    still returning a bare `[]`. A worker whose origin/main ref is missing (a
    fresh or re-imaged clone) or whose queue file moved prints "queue empty for
    me" once a minute, forever, with work waiting.
    """
    tasks, out = queue_head_with(0, FakeRun(128, "", "fatal: invalid object name"))
    check("queue: an unreadable queue yields no tasks", tasks == [])
    check("queue: and SAYS it could not read it, rather than nothing",
          "CANNOT READ" in out and "NOT an empty queue" in out)

    tasks, out = queue_head_with(0, FakeRun(0, "tasks:\n  - id: t1\n    node: n\n"))
    check("queue: a good read still returns its tasks",
          [t["id"] for t in tasks] == ["t1"])
    check("queue: and a good read stays quiet", "CANNOT READ" not in out)

    tasks, out = queue_head_with(0, FakeRun(0, "tasks: []\n"))
    check("queue: a genuinely empty queue is not shouted about",
          tasks == [] and "CANNOT READ" not in out and "DOES NOT PARSE" not in out)


def test_a_malformed_queue_does_not_kill_the_daemon():
    """A bad indent in farm-queue.yaml raised straight through main().

    yaml.safe_load's exception had no handler anywhere above it, so one lane
    pushing a queue that does not parse ended unattended rendering on the 5090
    until a human logged in — loud taken too far, since the queue is fixable in
    one push but nothing was left running to notice the fix.
    """
    bad = FakeRun(0, "tasks:\n  - id: t1\n   node: badly-indented\n\t- tab\n")
    try:
        tasks, out = queue_head_with(0, bad)
    except Exception as exc:                          # noqa: BLE001
        check("queue: a malformed queue does not raise out of queue_head (%s)"
              % type(exc).__name__, False)
        return
    check("queue: a malformed queue yields no tasks", tasks == [])
    check("queue: and says it does not parse, not that it is empty",
          "DOES NOT PARSE" in out)


def git(repo: Path, *args) -> None:
    import subprocess
    subprocess.run(("git",) + args, cwd=repo, check=True, capture_output=True,
                   text=True, encoding="utf-8", errors="replace")


def test_a_heartbeat_that_never_committed_does_not_pass_for_delivered():
    """Courier.mark checked its push and not its commit.

    All four git calls in mark() ran with `check=False` and only the push read
    its result, so a failed commit — an index.lock held by one of the other lanes
    sharing this checkout is the everyday way to get one — let the push succeed
    against the PREVIOUS state and print nothing. Silence from the courier reads
    as delivered, and the branch quietly stops advancing while the worker goes on
    rendering. It is the same lesson the push learned on 2026-08-01, one call
    earlier; box_runner's courier has checked this since it was written.
    """
    import farm_worker as fw

    real_repo = fw.REPO
    try:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            fw.REPO = repo
            git(repo, "init", "-q", "-b", "main")
            git(repo, "config", "user.email", "t@example.com")
            git(repo, "config", "user.name", "t")
            (repo / "seed.txt").write_text("seed\n")
            git(repo, "add", "seed.txt")
            git(repo, "commit", "-qm", "seed")

            c = fw.Courier("testbox")
            c.out = repo / "farm-out"

            # a held index.lock is what a peer lane mid-commit looks like.
            # git's own "Unable to create index.lock" on stderr below is the
            # POINT of this test, not a broken run — mark() is meant to survive
            # it and say so.
            print("    (the two git index.lock fatals below are deliberate)")
            (repo / ".git" / "index.lock").write_text("held by another lane\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.mark("STARTED task=t-1")
            out = buf.getvalue()
            check("courier: a failed heartbeat commit is reported, not swallowed",
                  "HEARTBEAT COMMIT FAILED" in out)

            (repo / ".git" / "index.lock").unlink()
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.mark("STARTED task=t-2")
            out = buf.getvalue()
            check("courier: a commit that works says nothing about committing",
                  "HEARTBEAT COMMIT FAILED" not in out)
            # the push has no remote here and must still be the loud one
            check("courier: and an undeliverable push is still loud",
                  "PUSH FAILED" in out)
    finally:
        fw.REPO = real_repo


# ------------------------------------------------------- publish_farm_out

def test_a_publish_glob_that_matches_nothing_cannot_write_a_manifest():
    """"published 0 file(s) + manifest" was the sound of three lost beats.

    Every job spec's publish step was six lines of inline python: glob, copy
    loop, write manifest, assert the count. With a glob that matches nothing the
    copy loop does not run, and the manifest is STILL written -- zero lines, zero
    pixels, one directory in farm-out that looks published. The count assertion
    fires after the file is on disk, so the empty manifest outlives the failure,
    and the publish step usually carries allow_fail so the exit code is discarded
    too. On 2026-08-14 beats 12, 18 and 21 globbed `12-wave1-s*` at files named
    `12-related-wave1-s*` -- the beat slug -- and all three published nothing,
    silently, permanently.

    WHAT WOULD THIS PRINT IF THE THING IT READS WERE COMPLETELY BROKEN? The old
    answer was "published 0 file(s) + manifest", exit 0 under allow_fail. The new
    answer must be rc=95 and an untouched destination.
    """
    import publish_farm_out as pfo

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = root / "out-b12-scene"
        src.mkdir()
        for s in range(4):
            (src / ("12-related-wave1-s%d.png" % s)).write_text("px", encoding="utf-8")
            (src / ("12-related-wave1-s%d.yaml" % s)).write_text("m", encoding="utf-8")
        dst = root / "ep2-b12-scene-0814"

        # the real 2026-08-14 glob: correct beat, correct tail, no slug
        buf = io.StringIO()
        rc = pfo.publish(str(dst), [str(src / "12-wave1-s*.*")], expect=8, out=buf)
        out = buf.getvalue()
        check("publish: a zero-match pattern is rc=95, not a success",
              rc == pfo.RC_PUBLISHED_NOTHING)
        check("publish: and it writes no manifest at all",
              not dst.exists() or list(dst.iterdir()) == [])
        check("publish: the failure says PUBLISHED NOTHING out loud",
              "PUBLISHED NOTHING" in out)
        check("publish: it lists what the sampler actually wrote",
              "12-related-wave1-s0.png" in out)
        check("publish: and it names the missing beat slug as the cause",
              "SLUG" in out and "FIX THE SPEC" in out)

        # the same call with the slug present must still work
        buf = io.StringIO()
        rc = pfo.publish(str(dst), [str(src / "12-related-wave1-s*.*")],
                         expect=8, manifest_name="ep2-b12-scene-0814.sha256",
                         out=buf)
        man = dst / "ep2-b12-scene-0814.sha256"
        check("publish: the correct pattern still publishes", rc == 0)
        check("publish: 8 files land beside an 8-line manifest",
              man.is_file()
              and len(man.read_text(encoding="utf-8").strip().splitlines()) == 8
              and len(list(dst.glob("12-related-wave1-s*.png"))) == 4)


def test_a_partial_publish_is_never_attested_by_a_manifest():
    """A manifest is a claim about a complete set, so a short set writes none.

    The old step wrote the manifest and then compared the count, which meant a
    6-of-8 publish left a 6-line manifest on disk claiming to describe the job.
    The comparison has to happen first or it is decoration.
    """
    import publish_farm_out as pfo

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = root / "out"
        src.mkdir()
        for s in range(3):
            (src / ("12-related-wave1-s%d.png" % s)).write_text("px", encoding="utf-8")
        dst = root / "ep2-b12-scene-0814"

        buf = io.StringIO()
        rc = pfo.publish(str(dst), [str(src / "12-related-wave1-s*.png")],
                         expect=4, out=buf)
        check("publish: 3-of-4 is rc=92, a partial render, not a pass",
              rc == pfo.RC_ARTIFACTS_MISSING)
        check("publish: a partial set leaves no manifest behind",
              not dst.exists() or list(dst.iterdir()) == [])
        check("publish: and the shortfall is stated as a count",
              "--expect 4" in buf.getvalue() and "matched 3" in buf.getvalue())


def test_the_publish_rcs_are_the_runners_rcs_and_not_new_numbers():
    """One RC TABLE. A second definition of 95 is how 93 collided in the first place."""
    import box_runner
    import publish_farm_out as pfo

    check("publish: RC_PUBLISHED_NOTHING is box_runner's 95",
          pfo.RC_PUBLISHED_NOTHING is box_runner.RC_PUBLISHED_NOTHING
          and pfo.RC_PUBLISHED_NOTHING == 95)
    check("publish: RC_ARTIFACTS_MISSING is box_runner's 92",
          pfo.RC_ARTIFACTS_MISSING is box_runner.RC_ARTIFACTS_MISSING
          and pfo.RC_ARTIFACTS_MISSING == 92)


def main() -> int:
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for fn in tests:
        print(fn.__name__)
        fn()
    print()
    if FAILURES:
        print("%d FAILED: %s" % (len(FAILURES), ", ".join(FAILURES)))
        return 1
    print("silent-gate guards: %d checks passed" % PASSED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
