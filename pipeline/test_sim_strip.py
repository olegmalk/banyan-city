#!/usr/bin/env python3
"""Pure-logic tests for the studio page's summary strip and bandwidth stat.

Both things these cover are the kind that rot silently rather than crash.

The bandwidth figure is a PROXY for a number this account cannot read — Vercel's
usage API is Pro/Enterprise only — so the page's honesty rests entirely on what
the proxy counts and on what it does when it cannot count. A regression here
would not raise; it would publish a confident wrong number, which is the one
outcome the whole design is arranged against.

Run as its own step and read the exit code. No network, no build, no _site.
"""
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sim as S  # noqa: E402

FAILS = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok ' if ok else 'FAIL'} {name}")
    if not ok:
        FAILS.append(f"{name}: got {got!r}, wanted {want!r}")


def check_true(name, got):
    ok = bool(got)
    print(f"  {'ok ' if ok else 'FAIL'} {name}")
    if not ok:
        FAILS.append(f"{name}: not true")


def _mkvideo(p: Path, size: int):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\0" * size)


print("bytes_words — a size a person can read")
check("gigabytes keep two decimals", S.bytes_words(3 * 1024 ** 3), "3.00 GB")
check("megabytes are whole", S.bytes_words(5 * 1024 ** 2), "5 MB")
check("kilobytes are whole", S.bytes_words(4 * 1024), "4 kB")
check("small numbers stay bytes", S.bytes_words(12), "12 bytes")

print("\nvideo_payload — counts the published show, and nothing else")
with tempfile.TemporaryDirectory() as td:
    out = Path(td)
    # what the site publishes: video inside a genome's leaves/
    _mkvideo(out / "sapling" / "leaves" / "001-t3-a.mp4", 1000)
    _mkvideo(out / "sapling" / "leaves" / "002-t2-a.webm", 500)
    # what it must NOT count: the unlisted review area and the trial clips are
    # copied to the deploy AFTER this page is built, so counting them would make
    # the figure depend on which build command produced it.
    _mkvideo(out / "review" / "ep1-v31-animated.mp4", 9_000_000)
    _mkvideo(out / "trials" / "wan-api" / "A.mp4", 8_000_000)
    # nor the takes gallery, which is neither in leaves/ nor on the watch path
    _mkvideo(out / "sapling" / "shots-takes" / "b01-r5.mp4", 7_000_000)
    # nor a non-video file that happens to live in leaves/
    (out / "sapling" / "leaves" / "001-t1-a.html").write_text("x" * 4242)

    pay = S.video_payload(out)
    check("the walk succeeds", pay["ok"], True)
    check("only the two leaf videos are counted", pay["count"], 2)
    check("and only their bytes", pay["bytes"], 1500)
    check("the largest is named", pay["biggest"], "001-t3-a.mp4")
    check("with its own size", pay["biggest_bytes"], 1000)

print("\nvideo_payload — fails soft, and never invents a zero")
missing = S.video_payload(Path("/nonexistent-path-for-this-test/_site"))
check_true("a directory that is not there does not raise", isinstance(missing, dict))
check("and reports itself as unmeasured", missing.get("ok"), False)
check_true("with a reason in words", bool(missing.get("why")))

print("\nthe glance strip carries no bandwidth tiles — the 2026-08-11 revamp")
# The two bandwidth figures sat in the summary strip as tiles and both audits
# called them trivia at glance level ("318 MB video per full watch · estimate
# 5 kB/s render box, mid-render" was the stranger's single most confusing
# line). The tiles are gone; the SECTIONS below keep every caveat.
check_true("the site-payload tile function is gone with the tile",
           not hasattr(S, "bandwidth_tile"))
check_true("and so is the render-box one", not hasattr(S, "render_bw_tile"))

print("\nthe section always carries the caveat, measured or not")
for label, pay in (("measured", {"ok": True, "bytes": 1024 ** 3, "count": 1,
                                 "biggest": "a.mp4", "biggest_bytes": 1024 ** 3}),
                   ("unmeasured", {"ok": False, "why": "boom"})):
    html = S.bandwidth_html(pay)
    check_true(f"{label}: says it is an estimate, not a measurement",
               "not a measurement" in html)
    check_true(f"{label}: names the Vercel dashboard as the real source",
               "Vercel dashboard" in html)
    check_true(f"{label}: says the Pages mirror publishes no figures",
               "GitHub Pages" in html)

print("\nstrip_counts — the same answer the record below prints")
# queue_entry_state is the page's one authority on an entry's state; the strip
# calls it rather than re-deriving, so a glance cannot contradict its own detail.
queue = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
backlog = [{"id": "d", "gate": "founder"}, {"id": "e"}]
counts = S.strip_counts(queue, backlog, [])
check("three unblocked tasks read runnable", counts["runnable"], 3)
check("a gated backlog entry reads blocked", counts["blocked"], 1)
check("an ungated one reads planned", counts["planned"], 1)
check("nothing is running without a check-in line", counts["running"], 0)
check("and nothing has failed", counts["failed"], 0)
check("every state the page knows has a count",
      sorted(counts) == sorted(S.QSTATES), True)

# ---- the render box's own bandwidth -------------------------------------------
# Roman asked how much of the household internet the 5090 eats making videos.
# The answer is "almost none", and an answer that agreeable is exactly the one to
# nail down: if the file ever fails to load, a plausible-looking 0 kB/s would
# CONFIRM the finding while measuring nothing at all. So the tests below care
# less about the numbers than about what happens when there are none.
print("\nrate_words — a speed a person can read")
check("a kilobyte a second", S.rate_words(4777), "5 kB/s")
check("and a megabyte a second", S.rate_words(3 * 1024 ** 2), "3 MB/s")

print("\nrender_bandwidth — the measurements load, and fail soft when they don't")
rb = S.render_bandwidth()
check_true("the committed measurements parse", rb.get("ok"))
check_true("and carry the date they were taken", bool(rb.get("measured_on")))
gone = S.render_bandwidth("pipeline/measured/no-such-file-for-this-test.yaml")
check("a missing file is not ok", gone.get("ok"), False)
check_true("and says why", bool(gone.get("why")))

print("\nrender_bandwidth_html — the finding leads, the workings follow")
sec = S.render_bandwidth_html(rb)
check_true("states the verdict in words", "not</b> what slows the internet" in sec)
check_true("names the thing that actually does", "downloading a new" in sec)
check_true("shows the idle control next to the render figure",
           "doing nothing" in sec)
check_true("and cites the file the numbers came from", S.RENDER_BW_FILE in sec)
sec_bad = S.render_bandwidth_html({"ok": False, "why": "boom"})
check_true("an unreadable measurement prints no rate", "kB/s" not in sec_bad)
check_true("and says so instead", "could not be" in sec_bad)

# The two bandwidth figures answer different questions — visitors' downloads vs
# the render box's own traffic — and their sections still may not blur into
# each other now that both live under one footprint heading.
pay_ok = {"ok": True, "bytes": 322_352_698, "count": 32,
          "biggest": "ep1.mp4", "biggest_bytes": 40_000_000}
check_true("the site figure still calls itself an estimate",
           "estimate" in S.bandwidth_html(pay_ok))
check_true("and the box section still calls its numbers measured",
           "real samples" in S.render_bandwidth_html(rb))

# ---- what the strip must NOT carry --------------------------------------------
# The laptop's free disk had a tile here for a few hours on 2026-08-11 and Roman
# took it off: "isnt this a bit much? people looking at this other than me will
# be confused, and it doesnt really need to be there." The 2026-08-11 revamp
# extended that ruling to the whole disk section — the same objection applies
# verbatim — and rebuilt the strip around the three questions a visitor brings:
# is it alive, what got made, where is the show. The measurement itself is
# still collected (box_cache.py disk) — dropping a tile is not licence to stop
# measuring.
print("\nthe strip is a visitor's glance, not the operator's housekeeping")
now = datetime.now(timezone.utc)
view = {"fin": [], "live": [], "unread": [], "last_activity": None,
        "by_id": {}, "inbox": [],
        "hero": {"number": 1, "watch": "watch.html"},
        "tot": {"final": 14, "total": 15}, "ep2": None}
strip = S.summary_strip(view, now)
check_true("no laptop-disk tile in the strip", "laptop disk free" not in strip)
check_true("and no link down to a disk section from it", '#disk"' not in strip)
check_true("no bandwidth trivia at glance level either",
           "kB/s" not in strip and "per full watch" not in strip)
check_true("it states the instant of the snapshot", "snapshot as of" in strip)
check_true("and never claims to be live", "claims to be live" in strip)
check_true("a studio with no readable activity reads quiet, not dead-certain",
           "quiet" in strip)
check_true("the disk reading is still collected", isinstance(S.local_disk(), dict))
check_true("...but its section left the public page with the tile",
           not hasattr(S, "local_disk_html"))

print("\nthe strip is keyed to last activity, never to this-exact-minute")
fresh = dict(view)
fresh["fin"] = [(now - timedelta(minutes=19), "the big render house",
                 "ep2-b05-warmfield-0811-1786470001", "")]
fresh["last_activity"] = now - timedelta(minutes=19)
strip2 = S.summary_strip(fresh, now)
check_true("fresh activity reads active off the log's own clock",
           "active" in strip2)
check_true("the newest job is translated into a stranger's words",
           "a fresh frame for episode 2, scene 05" in strip2)
check_true("...and its id never reaches the page",
           "ep2-b05-warmfield" not in strip2)
check_true("a log that could not be read never prints a zero",
           "not read" in S.summary_strip(dict(view, unread=["farm-results-hand"]),
                                         now))


# ---- the author has to be able to FIND what is waiting on him -----------------
# Roman, 2026-08-12: "i cannot find things to review on banyan.city/status." The
# inbox page had been live for hours; nothing on the page he lands on pointed at
# it. The link is the fix, so the link is what these guard — a strip that builds
# fine while carrying no route to the inbox is the exact regression.
#
# THE ROUTE IS `/review`, NOT `/review/inbox`. These asserted the older path and
# had been failing red ever since the board took over /review on 2026-08-14
# ("then how about you just move everything from /review/inbox to /review?") —
# the code was right and the test was the stale thing. A red test beside this
# section is worse than no test: it is where a real regression would hide.
print("\nthe glance carries the author's own inbox, and the way into it")
rev = S.summary_strip(dict(view, review_open=7), now)
check_true("the strip links to the review board", 'href="review"' in rev)
check_true("and prints how many are open", ">7<" in rev)
check_true("in words a stranger can read", "waiting on the author" in rev)
check_true("the author's cell comes before the visitor's questions",
           rev.index('href="review"') < rev.index("the studio"))
check_true("an empty inbox still offers the way in",
           'href="review"' in S.summary_strip(dict(view, review_open=0), now))
check_true("an unreadable inbox prints no count, and never a zero",
           "not read" in S.summary_strip(dict(view, review_open=None), now))

# Fail-soft, the box-queue rule one file over: missing or malformed comes back
# None so the tile says so in words. A build that dies here takes the whole site
# down over a yaml nobody deploys.
with tempfile.TemporaryDirectory() as td:
    real = S.REPO
    try:
        S.REPO = Path(td)
        check("no inbox yaml at all reads as unknown, not zero",
              S.review_inbox_open(), None)
        (Path(td) / "review").mkdir()
        (Path(td) / "review/inbox.yaml").write_text("- what: x\n  kind: ]\n[")
        check("unparseable reads as unknown too", S.review_inbox_open(), None)
        (Path(td) / "review/inbox.yaml").write_text("nope: a mapping")
        check("the wrong shape reads as unknown too", S.review_inbox_open(), None)
        (Path(td) / "review/inbox.yaml").write_text(
            "- what: a\n- what: b\n  resolved:\n    date: '2026-08-12'\n")
        check("a resolved entry is not waiting on anyone", S.review_inbox_open(), 1)
    finally:
        S.REPO = real

# The count on the tile and the count on the page it links to are the same test
# applied to the same file, so they cannot drift — that is why the tile reads the
# yaml and not the rendered html.
check_true("the real inbox yaml is readable by this build",
           isinstance(S.review_inbox_open(), int))

print()
if FAILS:
    print(f"✗ {len(FAILS)} failure(s)")
    for f in FAILS:
        print(f"   {f}")
    sys.exit(1)
print("✓ all summary-strip tests passed")
