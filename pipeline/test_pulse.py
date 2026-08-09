#!/usr/bin/env python3
"""Tests for the pulse cache and the graphs drawn from it.

Pure functions, no network and no git: the collector's git calls are the part
that cannot be unit-tested honestly, so everything downstream of them takes
plain data instead. Run: python3 pipeline/test_pulse.py

WHAT THESE ARE ACTUALLY GUARDING. Every failure this file catches is the same
failure — a missing reading rendered as a real one. A chart cannot say "I don't
know": it draws a line at some height, and zero is a height. So the absent
`backlog:` list, the unreachable box, the five minutes nobody sampled and the
half of the window older than the cache all have to survive as nulls from the
git blob to the SVG path, and each of those hops gets a test. The bug is not
hypothetical: the first build of this page drew four flat days of "nothing was
planned" over a week when planning simply lived elsewhere, and 68 minutes of
GPU work over a 24-hour cache reported as 2.4% of a 48-hour window.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pulse as bp
import pulse_series as ps

FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


# ---- the collector -------------------------------------------------------------

def test_absent_list_is_not_an_empty_one():
    """`backlog:` missing → None. `backlog:` present with no entries → 0."""
    both = "tasks:\n- id: a\n- id: b\nbacklog:\n- id: c\n"
    check("counts entries under each list", ps.count_entries(both) == (2, 1))

    no_backlog = "tasks:\n- id: a\n"
    check("a file with no backlog: reads None, not 0",
          ps.count_entries(no_backlog) == (1, None))

    empty_backlog = "tasks:\n- id: a\nbacklog:\n"
    check("an empty backlog: reads 0, not None",
          ps.count_entries(empty_backlog) == (1, 0))

    check("a file with neither list reads None twice",
          ps.count_entries("# just a comment\n") == (None, None))


def test_a_top_level_key_closes_the_list():
    """An entry only counts while we are inside the list it belongs to."""
    text = ("tasks:\n- id: a\n- id: b\n"
            "notes:\n- id: not-a-task\n"
            "backlog:\n- id: c\n")
    check("a following top-level key ends the list", ps.count_entries(text) == (2, 1))


def test_heartbeat_lines_get_the_right_day():
    """The boxes log HH:MM:SSZ and no date; the commit that carried the line
    supplies it, and must not throw a night's work onto the wrong day."""
    import datetime as dt

    def utc(y, m, d, hh, mm, ss=0):
        return int(dt.datetime(y, m, d, hh, mm, ss, tzinfo=dt.timezone.utc).timestamp())

    commit = utc(2026, 8, 9, 12, 5)
    check("a line minutes before its commit keeps that day",
          ps.stamp(12, 0, 0, commit) == utc(2026, 8, 9, 12, 0))

    # 23:58 published in the first minutes of the next day: yesterday's line.
    commit = utc(2026, 8, 10, 0, 3)
    check("a line just before midnight belongs to the previous day",
          ps.stamp(23, 58, 0, commit) == utc(2026, 8, 9, 23, 58))

    # A line can never be newer than the push that published it.
    commit = utc(2026, 8, 9, 6, 0)
    check("a time later in the commit's own day resolves backwards, never forwards",
          ps.stamp(22, 0, 0, commit) == utc(2026, 8, 8, 22, 0))


def test_downsample_reduces_without_inventing():
    tel = {
        "t": [0, 60, 120, 180, 240,  300, 360],
        "u": [10, 20, 30, 40, 50,    None, None],
        "up": [90, 20, 30, 40, 50,   None, None],
        "v": [1, 1, 1, 1, 1,         None, None],
        "r": [2, 2, 2, 2, 2,         None, None],
        "c": [3, 3, 3, 3, 3,         None, None],
    }
    out = ps.downsample(tel)
    check("one five-minute bucket from five minutes of samples", set(out) == {0})
    check("means are averaged", out[0]["u"] == 30)
    check("peaks are maxed, not averaged", out[0]["up"] == 90)
    check("a bucket whose every minute was null is absent, not zero",
          300 not in out)


def test_merge_is_idempotent_and_keeps_gaps():
    now = 100000
    first = ps.merge_grid({}, {0: {"u": 5, "up": 9, "v": 1, "r": 2, "c": 3}}, now)
    check("a fresh grid starts at its first bucket", first["t0"] == 0)

    again = ps.merge_grid(first, {0: {"u": 5, "up": 9, "v": 1, "r": 2, "c": 3}}, now)
    check("merging the same bucket twice changes nothing", again["u"] == first["u"])

    # A bucket two slots later, with the slot between never seen.
    later = ps.merge_grid(first, {600: {"u": 7, "up": 8, "v": 1, "r": 2, "c": 3}}, now)
    check("an unseen slot between two seen ones stays null",
          later["u"] == [5, None, 7])

    fresher = ps.merge_grid(later, {0: {"u": 6, "up": 9, "v": 1, "r": 2, "c": 3}}, now)
    check("a later reading of the same bucket wins", fresher["u"][0] == 6)


def test_retention_drops_the_far_past():
    now = 10 * 86400
    old = ps.merge_grid({}, {0: {"u": 5, "up": 5, "v": 1, "r": 1, "c": 1}}, now)
    check("a bucket older than the retention window is dropped",
          old["t0"] is None and old["u"] == [])


# ---- the charts ----------------------------------------------------------------

def test_a_gap_breaks_the_line():
    runs = bp._runs([(0, 1), (1, 2), (2, None), (3, 4), (4, 5)])
    check("a null splits one series into two drawn runs", len(runs) == 2)
    check("the runs hold only measured points",
          runs[0] == [(0, 1), (1, 2)] and runs[1] == [(3, 4), (4, 5)])
    check("an all-null series draws nothing at all",
          bp._runs([(0, None), (1, None)]) == [])


def test_queue_steps_hold_but_nulls_do_not():
    now = 1000
    samples = [[100, 2, None], [200, 5, 7]]

    runnable = bp.queue_points(samples, 1, 0, now, now)
    check("the last known depth is carried to the right edge",
          runnable[-1] == (now, 5))

    planned = bp.queue_points(samples, 2, 0, now, now)
    check("a null in the series survives into the points",
          any(v is None for _, v in planned))
    check("a series ending in a real value still extends to the edge",
          planned[-1] == (now, 7))

    only_null = bp.queue_points([[100, 1, None]], 2, 0, now, now)
    check("a series whose last reading is null is NOT carried to the edge",
          only_null == [(100, None)])


def test_a_sample_before_the_window_is_carried_in():
    """The queue had a depth at the left edge even if nobody committed there."""
    pts = bp.queue_points([[50, 4, 4], [500, 6, 6]], 1, 100, 1000, 1000)
    check("the depth in force at the window's start opens the line",
          pts[0] == (100, 4))


def test_null_tolerant_summaries():
    samples = [[1, 3, None], [2, None, 8], [3, 5, None]]
    check("last_known skips trailing nulls", bp.last_known(samples, 2) == 8)
    check("last_known returns None when nothing was ever recorded",
          bp.last_known([[1, None, None]], 1) is None)
    check("axis_top ignores nulls", bp.axis_top(samples, 2, 4) == 8)
    check("axis_top never returns below its floor", bp.axis_top(samples, 2, 20) == 20)
    check("axis_top survives an all-null column", bp.axis_top(samples, 1, 4) == 5)


def test_busy_minutes_counts_only_measured_slots():
    """The denominator bug, pinned. A 24-hour cache in a 48-hour window must
    report the share of the 24 hours it actually saw."""
    gpu = {"t0": 0, "bucket_seconds": 300,
           "u": [100, 100, None, None]}          # 2 measured slots, both flat out
    mins, measured, total = bp.busy_minutes(gpu, 0, 4 * 300)
    check("busy minutes are mean% × bucket length", mins == 10)
    check("measured counts only the slots carrying a reading", measured == 2)
    check("total counts every slot in the window", total == 4)
    check("100% over every measured slot is 100% of the card",
          round(mins / (measured * 5) * 100) == 100)


def test_idle_stretch_ends_at_a_gap():
    """An unreachable box is not an idle box, so a null must break the run."""
    gpu = {"t0": 0, "bucket_seconds": 300, "up": [0, 0, 0, 0]}
    hours, start = bp.idle_stretch(gpu, 0, 10 * 300)
    check("four idle slots are twenty idle minutes", round(hours * 60) == 20)
    check("the stretch reports when it began", start == 0)

    gapped = {"t0": 0, "bucket_seconds": 300, "up": [0, 0, None, 0, 0]}
    hours, _ = bp.idle_stretch(gapped, 0, 10 * 300)
    check("a gap splits an idle run rather than extending it",
          round(hours * 60) == 10)

    busy = {"t0": 0, "bucket_seconds": 300, "up": [0, 99, 0]}
    hours, _ = bp.idle_stretch(busy, 0, 10 * 300)
    check("a burst splits the run too", round(hours * 60) == 5)


def test_points_outside_the_window_are_left_out():
    gpu = {"t0": 0, "bucket_seconds": 300, "u": [1, 2, 3, 4]}
    pts = bp.gpu_points(gpu, "u", 300, 600)
    check("only buckets inside the window are returned",
          pts == [(300, 2), (600, 3)])
    check("a cache that does not reach the window yields no points",
          bp.gpu_points(gpu, "u", 100000, 200000) == [])


# ---- the page ------------------------------------------------------------------

def test_no_cache_says_so_and_draws_nothing():
    out = bp.render(None)
    check("a missing cache draws no chart", "<svg" not in out)
    check("a missing cache says so in words", "will not put a shape" in out)


def test_the_page_survives_a_hole_in_every_series():
    """Nothing here should raise, and nothing should print a None at a reader."""
    now = 1786300000
    data = {
        "generated": now - 60,
        "gpu": {"t0": now - 3600, "bucket_seconds": 300,
                "u": [None, 50, None], "up": [None, 90, None],
                "v": [None, 8, None], "vram_total_gb": 23.89,
                "gpu_name": "test card"},
        "queue": {"samples": [[now - 7200, 3, None]]},
        "jobs": {"events": [[now - 1800, "done", "rtx5090", "t"]], "branches": ["rtx5090"]},
    }
    out = bp.render(data, now=now)
    check("a sparse cache still draws charts", out.count("<svg") == 4)
    check("no None leaks into the reader's page", ">None<" not in out and " None " not in out)
    check("the page dates itself for the reader", "+04" in out)

    empty = bp.render({"generated": now, "gpu": {}, "queue": {"samples": []},
                       "jobs": {"events": [], "branches": []}}, now=now)
    check("an empty cache still renders a page", "<h1>The pulse</h1>" in empty)
    check("an empty chart says it is empty, not zero", "no GPU samples cached" in empty)


def test_the_page_never_divides_by_the_window():
    """Regression: the stat tile must quote the measured hours, not the axis."""
    now = 1786300000
    # Six hours of cache inside a 48-hour window, the card flat out throughout.
    n = 72
    data = {
        "generated": now,
        "gpu": {"t0": now - n * 300, "bucket_seconds": 300,
                "u": [100] * n, "up": [100] * n, "v": [10] * n,
                "vram_total_gb": 24, "gpu_name": "test card"},
        "queue": {"samples": []},
        "jobs": {"events": [], "branches": []},
    }
    out = bp.render(data, now=now)
    check("a card at 100% for every measured slot reads as 100%, not 12.5%",
          "100.0% of the card" in out)
    check("the tile names the hours it measured", "6 h measured" in out)


def main():
    test_absent_list_is_not_an_empty_one()
    test_a_top_level_key_closes_the_list()
    test_heartbeat_lines_get_the_right_day()
    test_downsample_reduces_without_inventing()
    test_merge_is_idempotent_and_keeps_gaps()
    test_retention_drops_the_far_past()
    test_a_gap_breaks_the_line()
    test_queue_steps_hold_but_nulls_do_not()
    test_a_sample_before_the_window_is_carried_in()
    test_null_tolerant_summaries()
    test_busy_minutes_counts_only_measured_slots()
    test_idle_stretch_ends_at_a_gap()
    test_points_outside_the_window_are_left_out()
    test_no_cache_says_so_and_draws_nothing()
    test_the_page_survives_a_hole_in_every_series()
    test_the_page_never_divides_by_the_window()

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} failure(s): " + "; ".join(FAILURES))
        return 1
    print("✓ all pulse tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
