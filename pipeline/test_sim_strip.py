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

print("\nthe tile says which of the two it is showing")
good = S.bandwidth_tile({"ok": True, "bytes": 322_352_698, "count": 32,
                         "biggest": "x.mp4", "biggest_bytes": 1})
check_true("a measured tile prints the size", "307 MB" in good)
check_true("and calls itself an estimate on its face", "estimate" in good)
check_true("and links down to the caveat", 'href="#bandwidth"' in good)
bad = S.bandwidth_tile({"ok": False, "why": "boom"})
check_true("an unmeasured tile says unavailable", "unavailable" in bad)
check_true("and prints no digits at all", not any(c.isdigit() for c in
                                                  bad.replace("bandwidth", "")))

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

print()
if FAILS:
    print(f"✗ {len(FAILS)} failure(s)")
    for f in FAILS:
        print(f"   {f}")
    sys.exit(1)
print("✓ all summary-strip tests passed")
