#!/usr/bin/env python3
"""Selftest for pipeline/safe_push.sh — the push guard.

The guard's whole value is what it REFUSES, and a refusal is invisible until
something tries it. So this builds a throwaway tree, drops stubs for `gh`, for
`git`, and for the two local gates onto PATH, and drives safe_push.sh through
every state it can meet: green, red, in-progress, in-progress-behind-red, a
gate that fails, and a gh that is missing or broken.

Nothing here touches the real repo, the real remote, or the network. Pure
stdlib, so it runs in CI beside the other suites.

The state the five lanes of 2026-08-20 actually pushed into is
`test_pending_on_red_refuses` — a run in flight with a failure behind it. A
one-row `gh run list -L1` reads that as "in progress, go ahead", which is why
this guard looks further back.
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SAFE_PUSH = os.path.join(ROOT, "safe_push.sh")

PASS = FAIL = 0
FAILURES = []


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  ok  %s" % label)
    else:
        FAIL += 1
        FAILURES.append(label)
        print("  FAIL %s" % label)


def _write_exe(path, body):
    with open(path, "w") as fh:
        fh.write(body)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def run_guard(runs, *, gate_rc=(0, 0), gh_mode="ok", args=("origin", "main")):
    """Run safe_push.sh in a sandbox. Returns (rc, stdout+stderr, pushed_args).

    `runs` is the JSON array `gh run list` will hand back.
    `gate_rc` is (lint_genome_rc, test_pipeline_rc).
    `gh_mode` is "ok" | "missing" | "error".
    """
    tmp = tempfile.mkdtemp(prefix="safepush-")
    try:
        pipe = os.path.join(tmp, "pipeline")
        binn = os.path.join(tmp, "bin")
        os.makedirs(pipe)
        os.makedirs(binn)
        shutil.copy(SAFE_PUSH, os.path.join(pipe, "safe_push.sh"))

        # --- the two local gates, faked so the suite stays fast (the real
        #     test_pipeline.py is ~27s; we are testing the wrapper, not it).
        for name, rc in (("lint_genome.py", gate_rc[0]),
                         ("test_pipeline.py", gate_rc[1])):
            with open(os.path.join(pipe, name), "w") as fh:
                fh.write("import sys\nprint('stub %s')\nsys.exit(%d)\n" % (name, rc))

        # --- git: records the push argv instead of performing it.
        pushlog = os.path.join(tmp, "pushed.txt")
        _write_exe(os.path.join(binn, "git"), (
            '#!/bin/sh\n'
            'if [ "$1" = "push" ]; then shift; printf "%s\\n" "$*" > ' + pushlog + '; fi\n'
            'exit 0\n'
        ))

        # --- gh: the whole point. Three behaviours.
        ghpath = os.path.join(binn, "gh")
        if gh_mode == "missing":
            pass  # simply never created; PATH is sealed below so the real gh is hidden
        elif gh_mode == "error":
            _write_exe(ghpath, '#!/bin/sh\necho "gh: not logged in\nto github.com" >&2\nexit 4\n')
        else:
            payload = os.path.join(tmp, "runs.json")
            with open(payload, "w") as fh:
                json.dump(runs, fh)
            _write_exe(ghpath, '#!/bin/sh\ncat %s\n' % payload)

        env = dict(os.environ)
        # Sealed PATH: only our stubs plus the interpreters the script needs.
        # Anything not stubbed must not silently resolve to the real tool.
        env["PATH"] = binn + os.pathsep + "/usr/bin" + os.pathsep + "/bin"
        env["SAFE_PUSH_PYTHON"] = sys.executable

        proc = subprocess.run(
            ["/bin/bash", os.path.join(pipe, "safe_push.sh")] + list(args),
            cwd=tmp, env=env, capture_output=True, text=True, encoding="utf-8",
            timeout=120,
        )
        pushed = None
        if os.path.exists(pushlog):
            with open(pushlog, encoding="utf-8") as fh:
                pushed = fh.read().strip()
        return proc.returncode, proc.stdout + proc.stderr, pushed
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_row(conclusion, status, rid, sha="abc123def", created="2026-08-20T19:00:00Z"):
    return {"conclusion": conclusion, "status": status, "databaseId": rid,
            "headSha": sha, "createdAt": created}


GREEN = [run_row("success", "completed", 111, created="2026-08-20T19:20:00Z"),
         run_row("success", "completed", 110, created="2026-08-20T19:10:00Z")]

RED = [run_row("failure", "completed", 32408510828, "5d1dbbf0e", "2026-08-20T19:24:39Z"),
       run_row("success", "completed", 32408192974, "8d20df316", "2026-08-20T19:21:08Z")]

INPROG = [run_row(None, "in_progress", 999, "cafe12345", "2026-08-20T19:30:00Z"),
          run_row("success", "completed", 111, "8d20df316", "2026-08-20T19:20:00Z")]

# The 2026-08-20 shape: a run in flight with a failure still behind it.
PENDING_ON_RED = [
    run_row(None, "in_progress", 32408979436, "a22714c55", "2026-08-20T19:29:54Z"),
    run_row("failure", "completed", 32408510828, "5d1dbbf0e", "2026-08-20T19:24:39Z"),
    run_row("success", "completed", 32408192974, "8d20df316", "2026-08-20T19:21:08Z"),
]


def test_green_pushes():
    print("\ngreen main")
    rc, out, pushed = run_guard(GREEN)
    check(rc == 0, "exit 0")
    check("CI green" in out, "says the CI is green")
    check(pushed == "origin main", "passed the args through to git push verbatim")
    check("SAFE-PUSH: PASS pushed" in out, "reports PASS")


def test_red_refuses():
    print("\nred main, no flag")
    rc, out, pushed = run_guard(RED)
    check(rc == 3, "exit 3 (refused on red)")
    check("main is red — fix it or wait; pushing now emails the founder" in out,
          "the refusal names the consequence")
    check(pushed is None, "NOTHING was pushed")
    check("32408510828" in out, "names the red run id so the lane can read it")


def test_red_with_fixing_main_pushes():
    print("\nred main, --fixing-main")
    rc, out, pushed = run_guard(RED, args=("--fixing-main", "origin", "main"))
    check(rc == 0, "exit 0 (the repair is allowed through)")
    check(pushed == "origin main", "--fixing-main is consumed, not forwarded to git")
    check("pushing the repair onto red main" in out, "says why it was allowed")


def test_in_progress_allows_and_names_the_run():
    print("\nrun in progress over green")
    rc, out, pushed = run_guard(INPROG)
    check(rc == 0, "exit 0 (stacking on green-so-far is normal)")
    check("999" in out, "prints the pending run id")
    check("in progress" in out, "says a run is in flight")
    check(pushed == "origin main", "pushed")


def test_pending_on_red_refuses():
    print("\nrun in progress, last COMPLETED run failed (the 2026-08-20 shape)")
    rc, out, pushed = run_guard(PENDING_ON_RED)
    check(rc == 3, "exit 3 — a pending run does not launder an older red")
    check(pushed is None, "NOTHING was pushed")
    check("32408979436" in out and "32408510828" in out,
          "names both the in-flight run and the red one behind it")


def test_cancelled_is_not_a_verdict():
    print("\nnewest completed run was cancelled")
    runs = [run_row("cancelled", "completed", 500, created="2026-08-20T19:40:00Z"),
            run_row("failure", "completed", 400, "5d1dbbf0e", "2026-08-20T19:24:39Z")]
    rc, out, pushed = run_guard(runs)
    check(rc == 3, "looks past the cancelled row to the red one behind it")
    check(pushed is None, "NOTHING was pushed")

    runs2 = [run_row("cancelled", "completed", 500, created="2026-08-20T19:40:00Z"),
             run_row("success", "completed", 400, created="2026-08-20T19:24:00Z")]
    rc2, out2, pushed2 = run_guard(runs2)
    check(rc2 == 0, "a cancelled run over green is not read as red either")
    check(pushed2 == "origin main", "pushed")


def test_local_gate_failure_refuses_before_touching_the_network():
    print("\nlocal gates")
    rc, out, pushed = run_guard(GREEN, gate_rc=(1, 0))
    check(rc == 2, "exit 2 when lint_genome fails")
    check(pushed is None, "NOTHING was pushed on a failed lint")
    check("local gate failed: lint_genome" in out, "names which gate failed")

    rc, out, pushed = run_guard(GREEN, gate_rc=(0, 1))
    check(rc == 2, "exit 2 when test_pipeline fails")
    check(pushed is None, "NOTHING was pushed on a failed test run")
    check("local gate failed: test_pipeline" in out, "names which gate failed")

    # --fixing-main overrides RED MAIN. It must never override your own broken tree.
    rc, out, pushed = run_guard(RED, gate_rc=(1, 0),
                                     args=("--fixing-main", "origin", "main"))
    check(rc == 2 and pushed is None,
          "--fixing-main does NOT waive the local gates")


def test_gh_unreachable_warns_but_does_not_strand_the_lane():
    print("\ngh missing or broken")
    for mode in ("missing", "error"):
        rc, out, pushed = run_guard(GREEN, gh_mode=mode)
        check(rc == 0, "%s: exit 0 — a gh outage is not evidence main is red" % mode)
        check("cannot read CI state" in out, "%s: warns loudly" % mode)
        check(pushed == "origin main", "%s: pushed" % mode)


def test_dry_run_and_arg_passthrough():
    print("\nplumbing")
    rc, out, pushed = run_guard(GREEN, args=("--dry-run", "origin", "HEAD:main"))
    check(rc == 0 and pushed is None, "--dry-run runs the checks and pushes nothing")
    check("would run: git push origin HEAD:main" in out, "--dry-run shows the command")

    rc, out, pushed = run_guard(
        GREEN, args=("origin", "main", "--force-with-lease"))
    check(pushed == "origin main --force-with-lease",
          "arbitrary git push flags survive the wrapper unchanged")

    rc, out, pushed = run_guard(GREEN, args=())
    check(rc == 0 and pushed == "", "bare `safe_push.sh` becomes a bare `git push`")


def test_no_runs_yet():
    print("\nempty history")
    rc, out, pushed = run_guard([])
    check(rc == 0, "a workflow with no runs is unknown, not red")
    check(pushed == "origin main", "pushed")


def main():
    print("safe_push.sh — push guard selftest")
    if not os.path.exists(SAFE_PUSH):
        print("MISSING %s" % SAFE_PUSH)
        return 1
    for fn in (test_green_pushes,
               test_red_refuses,
               test_red_with_fixing_main_pushes,
               test_in_progress_allows_and_names_the_run,
               test_pending_on_red_refuses,
               test_cancelled_is_not_a_verdict,
               test_local_gate_failure_refuses_before_touching_the_network,
               test_gh_unreachable_warns_but_does_not_strand_the_lane,
               test_dry_run_and_arg_passthrough,
               test_no_runs_yet):
        fn()
    print("\n%d passed, %d failed" % (PASS, FAIL))
    for f in FAILURES:
        print("  - %s" % f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
