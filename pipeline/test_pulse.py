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

import re
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
    # Counted as FIGURES, not as <svg> elements. The window selector gives each
    # figure one finished panel per offered window, so the number of svgs is a
    # property of how much history the cache holds and has no business in an
    # assertion about whether the four quantities are on the page.
    check("a sparse cache still draws all four charts", out.count('class="pchart') == 4)
    check("every chart carries at least one drawn window", out.count("<svg") >= 4)
    check("no None leaks into the reader's page", ">None<" not in out and " None " not in out)
    check("the page dates itself for the reader", "+04" in out)

    empty = bp.render({"generated": now, "gpu": {}, "queue": {"samples": []},
                       "jobs": {"events": [], "branches": []}}, now=now)
    check("an empty cache still renders a page", "<h1>The pulse</h1>" in empty)
    # THE INVARIANT, not the wording: with nothing cached the page must draw no
    # series at all and must say why in words. Which words is the page's business
    # and has changed once already; that a reader is never shown a line at zero
    # standing in for "we have no idea" is the thing worth failing a build over.
    check("an empty cache draws no series at all",
          'class="ln"' not in empty and 'class="fill"' not in empty)
    # More than one accepted phrase, deliberately. The page has said this two
    # ways — once per empty chart, and once as a greyed-out window selector —
    # and both are honest answers to "why is there nothing here". Pinning the
    # exact sentence would make a rewording look like a regression and tempt
    # whoever hits it to weaken the check that matters, which is the line above.
    said_why = any(p in empty for p in
                   ("does not reach back", "no GPU samples cached", "not cached"))
    check("an empty cache says why in words, rather than drawing zero", said_why)


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
          "100.0% of the card" in out and "% of the card" in out)
    check("no window dilutes the figure with time it could not see",
          "12.5% of the card" not in out and "50.0% of the card" not in out)
    # Read the denominator back out rather than matching a fixed string: the
    # tile is now printed once per offered window and formats its hours with a
    # decimal, and neither of those is the property under test. What is: no
    # tile may claim to have measured more hours than the cache actually holds.
    measured = [float(h) for h in re.findall(r"([\d.]+) h measured", out)]
    check("every tile names the hours it measured", bool(measured))
    check("no tile claims more measured hours than the cache holds",
          max(measured) <= 6.0 + 1e-9)
    check("the deepest window measures the whole six-hour cache",
          any(abs(h - 6.0) < 1e-9 for h in measured))


# ---- the time-window selector ---------------------------------------------------
# Roman, 2026-08-10: "status page UX is not production grade. in partucular there
# is no time window selection." What these guard is the honesty of the control
# rather than the control itself: a selector that offers a window the cache
# cannot fill turns "the machine was idle" and "we have no record" into the same
# blank rectangle, which is the one confusion this whole page exists to prevent.

def test_a_window_wider_than_the_cache_is_not_offered():
    now = 1786300000
    day = now - 24 * 3600            # a cache exactly one day deep, current
    menu = {h: (ok, why) for h, _l, _w, _s, ok, why in bp.window_menu(day, now, now)}

    check("an hour inside a one-day cache is offered", menu[1][0])
    check("the full day the cache holds is offered", menu[24][0])
    check("two days against a one-day cache is greyed out", not menu[48][0])
    check("a week against a one-day cache is greyed out", not menu[24 * 7][0])
    check("a greyed window says how far back the cache does reach",
          "only reaches back to" in menu[48][1])


def test_a_window_the_cache_nearly_covers_is_still_offered():
    """COVERAGE, not the whole span: 6.6 days of history should not lose the
    seven-day view over a missing sliver — it is a full picture, and the panel
    hatches the sliver."""
    now = 1786300000
    nearly = now - int(6.6 * 86400)
    menu = {h: ok for h, _l, _w, _s, ok, _y in bp.window_menu(nearly, now, now)}
    check("6.6 days of cache still offers the 7-day window", menu[24 * 7])

    thin = now - int(4 * 86400)
    menu2 = {h: ok for h, _l, _w, _s, ok, _y in bp.window_menu(thin, now, now)}
    check("4 days of cache does not offer the 7-day window", not menu2[24 * 7])


def test_a_stale_cache_does_not_offer_the_recent_windows():
    """A cache that stopped extending yesterday spans a week and still has
    nothing whatever to say about the last hour."""
    now = 1786300000
    menu = {h: (ok, why) for h, _l, _w, _s, ok, why
            in bp.window_menu(now - 8 * 86400, now - 20 * 3600, now)}
    check("the last hour is greyed out when nothing was cached in it", not menu[1][0])
    check("and it says the cache stopped rather than that it is shallow",
          "nothing has been cached since" in menu[1][1])
    check("the week, which the cache does cover, stays offered", menu[24 * 7][0])


def test_an_empty_cache_offers_no_window_at_all():
    now = 1786300000
    menu = bp.window_menu(None, None, now)
    check("no window is offered when there is nothing to draw",
          not any(ok for _h, _l, _w, _s, ok, _y in menu))
    check("and every button says so", all("nothing in the cache" in why
                                          for _h, _l, _w, _s, _ok, why in menu))


def test_the_span_with_no_cache_behind_it_is_struck_out():
    """The blank left-hand side of a wide window must not read as an idle
    machine. It is hatched, and the hatch is inside the plot where the shape is."""
    t0, t1 = 0, 10000
    band = bp.uncached_band(t0, t1, 5000)
    check("a record starting mid-window hatches the span before it",
          'class="hatch"' in band)
    check("and says in the plot that this is missing record, not missing work",
          "not cached" in band)

    check("a record older than the window hatches nothing",
          bp.uncached_band(t0, t1, -500) == "")
    check("a window with no known start hatches nothing",
          bp.uncached_band(t0, t1, None) == "")
    # A hole in the MIDDLE is a real measurement gap and keeps looking like one:
    # the band only ever covers the leading edge.
    band2 = bp.uncached_band(t0, t1, 9900)
    check("the hatch never reaches past the point the record starts",
          'class="hatch"' in band2 and 'width="0' not in band2)


def test_every_offered_window_is_drawn_into_the_page():
    """The selector may only offer panels that exist — it swaps finished charts
    and cannot draw one, so an offered window with no panel is a blank page."""
    now = 1786300000
    n = 24 * 12                       # 24 h of five-minute buckets
    data = {
        "generated": now,
        "gpu": {"t0": now - n * 300, "bucket_seconds": 300,
                "u": [50] * n, "up": [70] * n, "v": [8] * n,
                "vram_total_gb": 24, "gpu_name": "test card"},
        "queue": {"samples": [[now - 86400, 3, 5], [now - 3600, 4, 6]]},
        "jobs": {"events": [], "branches": []},
    }
    out = bp.render(data, now=now)
    offered = [h for h, _l, _w, _s, ok, _y
               in bp.window_menu(*bp.extent(data), now) if ok]
    check("a one-day cache offers the 1h, 6h and 24h windows",
          offered == [1, 6, 24])
    for h in offered:
        # four charts, so four panels per window
        check(f"the {h}h window is drawn on every chart",
              out.count(f'class="pwin" data-h="{h}"') == 4)
        check(f"the {h}h window has its own stat tiles",
              f'class="pstat" data-h="{h}"' in out)
    check("no panel is emitted for a window the selector greys out",
          'data-h="168"' not in out.split('class="pulse-grid"')[1])
    check("exactly one window is visible before anything is clicked",
          out.count('class="pwin" data-h="24"') == 4
          and out.count('class="pwin" data-h="24" hidden') == 0)


def test_the_selector_hides_itself_when_javascript_is_off():
    """A control that cannot work must not be on the page looking like it can.
    The bar ships hidden and the script unhides it."""
    now = 1786300000
    n = 300
    data = {
        "generated": now,
        "gpu": {"t0": now - n * 300, "bucket_seconds": 300,
                "u": [10] * n, "up": [20] * n, "v": [2] * n,
                "vram_total_gb": 24, "gpu_name": "test card"},
        "queue": {"samples": [[now - 3600, 1, 1]]},
        "jobs": {"events": [], "branches": []},
    }
    out = bp.render(data, now=now)
    bar = out[out.index('id="winbar"'):]
    check("the window bar is emitted hidden", bar[:bar.index(">")].endswith("hidden"))
    check("and a default chart is on the page regardless",
          '<svg' in out and 'class="pwin"' in out)
    check("the y axis is fixed across windows, not rescaled per pick",
          "does not move when the window does" in out)


def test_the_axis_ceiling_does_not_move_between_windows():
    """A queue axis rescaled per window would redraw a quiet hour as a busy one.
    Every panel of a chart must share one ceiling."""
    now = 1786300000
    samples = [[now - 6 * 86400, 20, 30], [now - 1800, 2, 3]]
    data = {
        "generated": now,
        "gpu": {},
        "queue": {"samples": samples},
        "jobs": {"events": [], "branches": []},
    }
    out = bp.render(data, now=now)
    # 20 is the deepest runnable reading ever taken, so it is the ceiling on
    # every window — including the recent ones where the queue never passed 2.
    tops = re.findall(r'text-anchor="end">(\d+)</text>', out)
    check("the deepest reading in the cache sets the ceiling",
          "20" in tops and "30" in tops)


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
    test_a_window_wider_than_the_cache_is_not_offered()
    test_a_window_the_cache_nearly_covers_is_still_offered()
    test_a_stale_cache_does_not_offer_the_recent_windows()
    test_an_empty_cache_offers_no_window_at_all()
    test_the_span_with_no_cache_behind_it_is_struck_out()
    test_every_offered_window_is_drawn_into_the_page()
    test_the_selector_hides_itself_when_javascript_is_off()
    test_the_axis_ceiling_does_not_move_between_windows()

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} failure(s): " + "; ".join(FAILURES))
        return 1
    print("✓ all pulse tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
