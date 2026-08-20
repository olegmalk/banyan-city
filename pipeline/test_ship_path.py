#!/usr/bin/env python3
"""Pure-logic tests for /status's "path to episode 2" section.

WHAT IS ACTUALLY AT RISK HERE, because it is not a crash. Every failure this
guards is a page that renders beautifully and says something false: a countdown
built from a cutoff that was never in the record, a "0 of 21 scenes" published
off a read that failed, an estimate printed with the word "measured" over it, or
a machine figure quietly added to the author's clock. None of those raise. They
publish.

So the checks below are mostly about REFUSAL — what the module declines to claim
when a file is missing, malformed, or says something it cannot support.

No network, no build, no _site, no git. Run as its own step and read the exit
code: piping to tail masks failures, and that has bitten this repo twice.
"""
import datetime
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ship_path as S  # noqa: E402

FAILS = []
UTC = datetime.timezone.utc


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


def _repo(tmp: Path, state: str = "", readiness=None, jobs=None,
          ship: dict = None) -> Path:
    """A miniature repo holding only what the module reads."""
    import yaml
    (tmp / "pipeline" / "measured").mkdir(parents=True, exist_ok=True)
    (tmp / "review" / "ep2-picks").mkdir(parents=True, exist_ok=True)
    (tmp / "STATE.md").write_text(state, encoding="utf-8")
    if readiness is not None:
        (tmp / "review/ep2-picks/cut-readiness-0819.yaml").write_text(
            yaml.safe_dump(readiness), encoding="utf-8")
    if jobs is not None:
        (tmp / "pipeline/measured/queue-history.json").write_text(
            json.dumps({"_meta": {"measured_at": "2026-08-20T15:00:00Z"},
                        "jobs": jobs}), encoding="utf-8")
    if ship is not None:
        d = tmp / "review" / "ep2-ship-0821" / "sources"
        d.mkdir(parents=True, exist_ok=True)
        (d / "ship-manifest.yaml").write_text(yaml.safe_dump(ship),
                                              encoding="utf-8")
    return tmp


ORDER_MD = """
## 2026-08-19 — something else entirely
not an order.

## 2026-08-20 — SHIP ORDER (founder): episode 2 ships within 24h
"ship it." Plan of record: best-available takes ship with named faults. Upgrade
cutoff: takes landing by 12:00 2026-08-21 enter the final cut; then assembly.

## 2026-08-20 — a later note that is not an order
"""

print("read_ship_order — the order, and what it refuses to invent")
with tempfile.TemporaryDirectory() as t:
    r = _repo(Path(t), ORDER_MD)
    o = S.read_ship_order(r)
    check("finds the newest SHIP ORDER heading", o["date"], "2026-08-20")
    check("parses the cutoff to an aware UTC datetime", o["cutoff"],
          datetime.datetime(2026, 8, 21, 12, 0, tzinfo=UTC))
    check("prints the cutoff in the record's own words", o["cutoff_text"],
          "12:00 on 2026-08-21")
    # The parenthetical actor is dropped: the page's own sentence already names
    # who gave the order, and printing it twice in one line is how that line got
    # rejected the first time.
    check("headline drops the (founder) parenthetical", o["headline"],
          "episode 2 ships within 24h")

with tempfile.TemporaryDirectory() as t:
    r = _repo(Path(t), "## 2026-08-20 — SHIP ORDER: ship it\nno time here.\n")
    o = S.read_ship_order(r)
    check_true("an order with no time is still an order", o.get("date"))
    check("...but it yields NO cutoff rather than a guessed one", o["cutoff"],
          None)
    st = S.steps(o, {}, {}, [], [], now=datetime.datetime(2026, 8, 20, tzinfo=UTC))
    check("...and step 1 says so instead of counting down", st[0]["estimate"],
          "no cutoff on record")

with tempfile.TemporaryDirectory() as t:
    check("no STATE.md at all is {} and not a crash",
          S.read_ship_order(Path(t) / "nope"), {})

print("the upgrade window is a derived state, never a declared one")
o = {"cutoff": datetime.datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
     "cutoff_text": "12:00 on 2026-08-21", "date": "2026-08-20"}
before = S.steps(o, {}, {}, [], [], now=datetime.datetime(2026, 8, 20, 15, 30, tzinfo=UTC))
after = S.steps(o, {}, {}, [], [], now=datetime.datetime(2026, 8, 21, 13, 0, tzinfo=UTC))
check("open before the cutoff", before[0]["state"], "flight")
check("...with the gap in it", before[0]["estimate"],
      "20h 30m left when this page was built")
check("closed after it, with no edit to anything", after[0]["state"], "done")
check("...and no negative countdown", after[0]["estimate"], "closed")
check("assembly waits on the window while it is open", before[1]["state"],
      "wait-machine")
check("...and is ready once it shuts", after[1]["state"], "ready")

print("the two clocks are never added, and the author's step is never measured")
check("the watch-through is the author's", before[2]["owner"], "you — the author")
for s in before:
    if s["owner"].startswith("you"):
        check_true(f"step {s['n']} is not claimed as measured", not s["measured"])
check("publishing waits on the author too", before[4]["state"], "wait-you")
check_true("five steps, no more and no fewer", len(before) == 5)

print("swap_minutes — today's runs, and silence when there are none")
now = datetime.datetime(2026, 8, 20, 15, 0, tzinfo=UTC)
fresh = [{"kind": "motion", "duration_s": 300, "finished_at": "2026-08-20T14:00:00Z"},
         {"kind": "motion", "duration_s": 360, "finished_at": "2026-08-20T14:30:00Z"},
         {"kind": "motion", "duration_s": 420, "finished_at": "2026-08-20T12:00:00Z"}]
m = S.swap_minutes(fresh, now)
check("median of the day's moving-picture jobs", round(m["minutes"], 2), 6.0)
check("...carrying its sample size", m["n"], 3)
stale = [{"kind": "motion", "duration_s": 300, "finished_at": "2026-08-01T14:00:00Z"}]
check("a job outside the window buys nothing", S.swap_minutes(stale, now), {})
check("and the step says so rather than borrowing another kind's number",
      S.steps(o, {}, {}, stale, [], now)[3]["estimate"], "not measured")
check("kind_median never substitutes a neighbouring kind",
      S.kind_median(fresh, "still"), {})

print("rollup — the join is outer, so a scene can never fall off the strip")
cut = {"beats": [{"n": 1, "slug": "COLD OPEN", "take": "01.mp4"},
                 {"n": 2, "slug": "THE SPRINT", "take": ""}]}
ready = {"beats": {1: {"n": 1, "slug": "COLD OPEN", "status": "PASS", "fault": ""},
                   2: {"n": 2, "slug": "THE SPRINT", "status": "best-available",
                       "fault": "never scored against a bar"},
                   3: {"n": 3, "slug": "BAD COVER", "status": "slate",
                       "fault": "no footage"}}}
rows = S.rollup(cut, ready, worked={1})
check("every scene either file knows about is on the strip", len(rows), 3)
check("footage plus a fresh attempt today reads as an upgrade", rows[0]["state"], "up")
check("no take in the cut is a slate", rows[1]["state"], "slate")
check("a scene the cut does not list is unknown, not missing", rows[2]["state"], "unk")
check("PASS is not a named fault", rows[0]["named_fault"], False)
check("anything else is", rows[1]["named_fault"], True)
check("named faults count what ships with a written reason",
      sum(1 for r in rows if r["named_fault"]), 2)

# A dated ledger and a newer cut can honestly disagree, and the page must not
# print the disagreement as a claim. A row still reading `slate` over a scene
# that now has footage has not been re-scored; "shipping as slate" beside a
# strip showing that scene filled is the page arguing with itself.
stale_rows = S.rollup({"beats": [{"n": 9, "slug": "THE PAUSE", "take": "09.mp4"}]},
                      {"beats": {9: {"n": 9, "slug": "THE PAUSE",
                                     "status": "slate", "fault": "no plate"}}},
                      worked=set())
check("a stale slate row is flagged", stale_rows[0]["stale"], True)
check("...and is not printed as a contradiction", stale_rows[0]["status"],
      "not re-scored since it got footage")
check("...but still counts as a fault, because it is not a clean pass",
      stale_rows[0]["named_fault"], True)

print("the ship cut: manifest first, the assembled cut's own record second")
with tempfile.TemporaryDirectory() as t:
    r = _repo(Path(t), ORDER_MD, ship={"beats": [
        {"beat": 1, "slug": "COLD OPEN", "take": "01.mp4"},
        {"beat": 2, "slug": "THE SPRINT", "take": None}]})
    c = S.read_ship_cut(r)
    check("reads the ship lane's manifest when it exists", c["source"], "manifest")
    check("...and both scenes come through", len(c["beats"]), 2)

with tempfile.TemporaryDirectory() as t:
    import yaml
    r = Path(t)
    _repo(r, ORDER_MD)
    d = r / "review" / "ep2-ship-0821"
    (d / "sources").mkdir(parents=True)
    (d / "ep2-ship-0821.mp4.meta.yaml").write_text(yaml.safe_dump({
        "beats": 3, "footage_beats": [1, 2], "slate_beats": [3],
        "duration_s": 116.08, "provisional_beats": [2],
        "sources": [{"beat": 1, "slug": "A", "clip": "01.mp4"},
                    {"beat": 2, "slug": "B", "clip": "02.mp4"},
                    {"beat": 3, "slug": "C", "clip": "03.mp4"}]}),
        encoding="utf-8")
    c = S.read_ship_cut(r)
    check("falls back to the cut's own sidecar", c["source"], "meta")
    # The sidecar lists a clip for every scene INCLUDING the slates, so the
    # slate list has to win. Trusting `sources` alone would publish "21 of 21
    # scenes have footage" over a cut with a title card in it.
    check("slate_beats overrides a clip named in sources",
          [b["take"] for b in c["beats"]][2], "")
    check("the cut's measured runtime comes through", c["runtime_s"], 116.08)
    st = S.steps({}, c, {}, [], [], now)
    check_true("...and reaches the watch-through's basis as 1:56",
               "1:56" in st[2]["basis"])

print("nothing renders off a failed read — and nothing renders a zero")
with tempfile.TemporaryDirectory() as t:
    r = Path(t)
    (r / "review").mkdir(parents=True)
    check("no sources at all -> empty section, not a false one",
          S.html(repo=r, now=now), "")
with tempfile.TemporaryDirectory() as t:
    # The brief's own case: the ship lane has not landed. The section must still
    # render the order and the plan, and must SAY the cut is pending.
    r = _repo(Path(t), ORDER_MD, jobs=[])
    h = S.html(repo=r, now=now)
    check_true("an order with no cut still renders the path", "The path to episode 2" in h)
    check_true("...and says the ship lane is still assembling",
               "still assembling" in h)
    check_true("...and claims no scene counts", "of 21 scenes" not in h)
    check_true("...and prints no beat strip it cannot fill", 'class="pbc' not in h)

print("the html says which of its numbers are measured")
with tempfile.TemporaryDirectory() as t:
    r = _repo(Path(t), ORDER_MD, readiness={"beats": [
        {"beat": n, "slug": f"S{n}", "status": "PASS" if n == 1 else "best-available",
         "blocked_on": "a judgement, not a render. More words after."}
        for n in range(1, 4)]}, jobs=fresh, ship={"beats": [
            {"beat": 1, "slug": "S1", "take": "01.mp4"},
            {"beat": 2, "slug": "S2", "take": "02.mp4"},
            {"beat": 3, "slug": "S3", "take": None}]})
    h = S.html(repo=r, now=now)
    check_true("every step says which kind of number it is",
               h.count("Measured:") + h.count("Estimate:")
               + h.count("On record:") == 5)
    # The cutoff is neither: it is a deadline somebody set, and it shipped once
    # under the word "Estimate", which is the page miscategorising a fact it
    # holds a written record of.
    check_true("the cutoff is On record, not an Estimate", "On record:" in h)
    check_true("the faults fold names its count", "2 named faults" in h)
    check_true("the fault line is the ledger's own first sentence",
               "a judgement, not a render" in h)
    check_true("...and is cut at the sentence, not mid-clause",
               "More words after" not in h)
    check_true("three scenes, three cells", h.count('class="pbc') == 3)
    check_true("all three tenses are on the page",
               all(x in h for x in ("What happened", "What is happening",
                                    "What is planned")))
    check_true("no raw beat jargon in the reader's copy", "beat 0" not in h.lower())

print("one_sentence — an elision is not a full stop")
check("a run of dots does not end the sentence",
      S.one_sentence("held by the ... ruling. Then more."),
      "held by the … ruling")
check("empty in, empty out", S.one_sentence(None), "")
check("long headlines are cut on a word boundary with an ellipsis",
      S.one_sentence("a " * 100, 20).endswith("…"), True)

print("minutes_words / gap_words — estimates, never dressed as measurements")
check("under ninety minutes reads flat", S.minutes_words(6), "6 min")
check("over it hedges", S.minutes_words(180), "about 3.0 h")
check("zero is nothing, not '0 min'", S.minutes_words(0), "")
check("a bad value is nothing", S.minutes_words(None), "")
check("hours and minutes", S.gap_words(datetime.timedelta(minutes=150)), "2h 30m")
check("minutes alone", S.gap_words(datetime.timedelta(minutes=42)), "42 min")
check("an expired gap is not negative", S.gap_words(datetime.timedelta(minutes=-5)),
      "none")

print("the real repo builds a section (no network, no _site)")
live = S.html()
check_true("it renders", len(live) > 500)
check_true("...as one section with the page's own id", 'id="path"' in live)
check_true("...and it is not a bare template", "steps to live" in live)

print()
if FAILS:
    print(f"✗ {len(FAILS)} failure(s)")
    for f in FAILS:
        print("   -", f)
    sys.exit(1)
print("✓ all checks pass")
