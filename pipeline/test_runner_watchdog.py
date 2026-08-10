#!/usr/bin/env python3
"""The watchdog's detection rule, driven directly — no ssh, no box.

The false positive matters more than the true positive here. A watchdog that
fires during a normal model load would kill healthy renders, and the load phase
is genuinely indistinguishable from idle on the GPU counters (an LTX job spends
~90s at 0% and 0 MiB loading a 24 GB text encoder). So most of these cases are
about NOT firing.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runner_watchdog import diagnose, STALL_SECONDS  # noqa: E402

CASES = [
    # (name, queue, big_process, log_age, should_fire)
    ("the 19:29 wedge: 12 queued, nothing claimed, log silent 16 min",
     {"ready": 12, "running": 0, "done": 94, "failed": 1}, False, 16 * 60, True),

    ("empty queue and a quiet log is CORRECT — this was the normal state for "
     "hours on 2026-08-10 and firing on it would restart a healthy runner",
     {"ready": 0, "running": 0, "done": 94, "failed": 1}, False, 40 * 60, False),

    ("model load: job claimed, log briefly quiet, GPU would read 0%/0MiB",
     {"ready": 5, "running": 1, "done": 94, "failed": 1}, False, 80, False),

    ("mid-render: no log line for 4 min but the process holds gigabytes",
     {"ready": 5, "running": 1, "done": 94, "failed": 1}, True, 4 * 60, False),

    ("inter-job gap: claimed nothing yet, log wrote 30s ago",
     {"ready": 5, "running": 0, "done": 94, "failed": 1}, False, 30, False),

    ("longest real job (SDXL still, 5m20s) must NOT trip the 8 min bar",
     {"ready": 5, "running": 0, "done": 94, "failed": 1}, False, 320, False),

    ("a render is resident but the queue drained — still not a wedge",
     {"ready": 0, "running": 1, "done": 94, "failed": 1}, True, 600, False),

    ("unreadable log is a broken probe, not evidence of a wedge",
     {"ready": 9, "running": 0, "done": 94, "failed": 1}, False, None, False),

    ("wedge with a single queued job still counts",
     {"ready": 1, "running": 0, "done": 94, "failed": 1}, False, 9 * 60, True),

    ("one second past the bar fires; one second under does not",
     {"ready": 3, "running": 0, "done": 94, "failed": 1}, False,
     STALL_SECONDS + 1, True),
    ("...and one second under",
     {"ready": 3, "running": 0, "done": 94, "failed": 1}, False,
     STALL_SECONDS - 1, False),
]


def main():
    bad = 0
    for name, q, big, age, want in CASES:
        got, why = diagnose(q, big, age)
        if got != want:
            bad += 1
            print(f"FAIL  {name}\n      expected fire={want} got={got} ({why})")
        else:
            print(f"ok    {name}")
    print()
    if bad:
        print(f"✗ {bad} watchdog case(s) failed")
        return 1
    print(f"✓ all {len(CASES)} watchdog cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
