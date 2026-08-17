#!/usr/bin/env python3
"""Guards on the episode ETA — the arithmetic, and the four things it must refuse.

Pure logic: yaml in, numbers out. No git, no network, no box, so this runs in CI
beside the other suites. Run: python3 pipeline/test_episode_eta.py

The failures worth catching here are all failures of CONFIDENCE, not of maths. A
missing measurement that renders as `0 h left`, a beat waiting on the author
counted as work for the card, an undecided beat billed as if it were certain to
be kept, a projection off one finished beat printed with the same face as one
off forty — every one of those produces a page that looks more finished than the
episode is, which is the direction this repo is not allowed to be wrong in.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import episode_eta as eta

REPO = Path(__file__).resolve().parent.parent
FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


def write(tmp: Path, name: str, text: str) -> str:
    p = tmp / name
    p.write_text(text, encoding="utf-8")
    return str(p)


# A four-beat episode with one of everything that matters: one finished, one
# waiting on the author, one we know how to fix, one nobody has decided about.
PROGRESS = """
episodes:
  - number: 2
    node: 002b-first-citizen
    total_beats: 4
    beats:
      - {n: 1, state: done}
      - {n: 2, state: candidate-awaiting-founder}
      - {n: 3, state: fix-known}
      - {n: 4, state: blocked-decision}
"""
ETA_YAML = """
measured_at: 2026-08-13 09:00Z
sidecar_window: 10 Aug - 13 Aug
episodes:
  - number: 2
    node: 002b-first-citizen
    finished_beats_sampled: 6
    rounds_median: {ltx: 4, still: 2}
"""
BOXQ = """
kind_medians: {ltx: 5.0, still: 1.0, charref: 2.9}
"""
# Real field names from review/inbox.yaml: `what`, `url`, `since`, and a
# `resolved:` block that appears only once the author has answered. No id.
INBOX = """
- what: Should beats 13-15 be cut?
  url: /review/ep2-picks/motion-0812
  since: 2026-08-12
  episode: 2
- what: Already answered
  url: /review/x
  since: 2026-08-11
  episode: 2
  resolved:
    date: '2026-08-12'
    verdict: keep it
- what: A different episode's call
  url: /review/y
  since: 2026-08-10
  episode: 1
- what: An open call nobody tagged to an episode
  url: /review/z
  since: 2026-08-09
"""


def _paths(tmp: Path):
    return dict(progress_path=write(tmp, "p.yaml", PROGRESS),
                eta_path=write(tmp, "e.yaml", ETA_YAML),
                box_path=write(tmp, "b.yaml", BOXQ),
                inbox_path=write(tmp, "i.yaml", INBOX))


def test_every_beat_lands_in_exactly_one_state(tmp: Path):
    r = eta.rows(**_paths(tmp))[0]
    check("all four beats are counted", sum(r["counts"].values()) == 4)
    check("one beat is founder-ready", r["ready"] == 1)
    check("one beat waits on the author", r["awaiting_founder"] == 1)
    check("one beat is firm machine work", r["needs_render"] == 1)
    check("one beat is undecided", r["conditional_beats"] == 1)


def test_a_beat_waiting_on_the_author_is_not_work_for_the_card(tmp: Path):
    # 1 fix-known beat x (4 ltx x 5.0 + 2 still x 1.0) = 22 min. The beat with a
    # candidate sitting in front of the author must add nothing: the card has
    # done its part and is idle, whatever the page says about the episode.
    r = eta.rows(**_paths(tmp))[0]
    check("per-beat minutes are rounds x kind medians", r["per_beat_minutes"] == 22.0)
    check("machine minutes bill only the fix-known beat", r["machine_minutes"] == 22)


def test_an_undecided_beat_is_costed_apart_from_the_certain_work(tmp: Path):
    r = eta.rows(**_paths(tmp))[0]
    check("the undecided beat is not in the firm figure", r["machine_minutes"] == 22)
    check("it is costed, separately", r["conditional_minutes"] == 22)
    check("and the two are never pre-added", r["machine_minutes"] != 44)


def test_a_missing_measurement_reads_as_unknown_and_never_as_zero(tmp: Path):
    p = _paths(tmp)
    # No kind medians to multiply by — the states are still known, the hours are
    # not, and `0 h of work left` would be the most confident possible lie.
    r = eta.rows(**dict(p, box_path=write(tmp, "empty.yaml", "{}")))[0]
    check("no job times → hours unknown", r["machine_minutes"] is None)
    check("no job times → per-beat unknown", r["per_beat_minutes"] is None)
    check("but the beat counts survive", r["ready"] == 1 and r["needs_render"] == 1)
    # No rounds median either.
    r2 = eta.rows(**dict(p, eta_path=write(tmp, "e2.yaml", "episodes: []")))[0]
    check("no rounds median → hours unknown", r2["machine_minutes"] is None)
    check("per_beat_minutes({}, meds) is None, not 0",
          eta.per_beat_minutes({}, {"ltx": 5.0}) is None)
    check("per_beat_minutes(rounds, {}) is None, not 0",
          eta.per_beat_minutes({"ltx": 4}, {}) is None)


def test_an_absent_or_broken_progress_file_produces_no_row_at_all(tmp: Path):
    check("missing file → no rows", eta.rows(progress_path=str(tmp / "nope.yaml")) == [])
    check("not a mapping → no rows",
          eta.rows(progress_path=write(tmp, "list.yaml", "- 1\n- 2")) == [])
    check("no beats → no rows",
          eta.rows(progress_path=write(tmp, "bare.yaml",
                                       "episodes:\n  - number: 2\n")) == [])
    check("unparseable → no rows",
          eta.rows(progress_path=write(tmp, "bad.yaml", "a: [1,\n  b: ]]")) == [])


def test_a_state_this_file_does_not_define_is_dropped_not_guessed(tmp: Path):
    # A typo'd state must not quietly become "nothing to render here". The beat
    # falls out of the counts and `counted` stops matching `total_beats`, which
    # is the discrepancy the report prints.
    doc = PROGRESS.replace("state: fix-known", "state: fix_known")
    r = eta.rows(**dict(_paths(tmp), progress_path=write(tmp, "typo.yaml", doc)))[0]
    check("the mislabelled beat is not counted", r["counted"] == 3)
    check("and it is not silently billed as done", r["ready"] == 1)
    check("the total still says four beats exist", r["total"] == 4)
    check("no work is claimed for it", r["needs_render"] == 0)


def test_a_thin_projection_says_so_and_still_prints(tmp: Path):
    doc = ETA_YAML.replace("finished_beats_sampled: 6", "finished_beats_sampled: 2")
    r = eta.rows(**dict(_paths(tmp), eta_path=write(tmp, "thin.yaml", doc)))[0]
    check("a two-beat sample is labelled thin", r["thin"] is True)
    check("and the arithmetic is printed anyway", r["machine_minutes"] == 22)
    r2 = eta.rows(**_paths(tmp))[0]
    check("a six-beat sample is not labelled thin", r2["thin"] is False)
    check("MIN_SAMPLE is the documented four", eta.MIN_SAMPLE == 4)


def test_the_gate_list_is_the_tagged_open_entries_and_says_what_it_missed(tmp: Path):
    r = eta.rows(**_paths(tmp))[0]
    said = [d["what"] for d in r["decisions"]]
    check("an open entry tagged to this episode is listed",
          "Should beats 13-15 be cut?" in said)
    check("a resolved entry is not", "Already answered" not in said)
    check("another episode's entry is not", "A different episode's call" not in said)
    check("an untagged entry is not attributed",
          "An open call nobody tagged to an episode" not in said)
    check("but untagged open entries are counted out loud",
          r["decisions_untagged"] == 1)
    check("each listed call carries the url the author clicks",
          r["decisions"][0]["url"] == "/review/ep2-picks/motion-0812")
    check("episode 1's own row gets episode 1's entry",
          [d["what"] for d in eta.rows(**dict(_paths(tmp), progress_path=write(
              tmp, "p1.yaml", PROGRESS.replace("number: 2", "number: 1")
          )))[0]["decisions"]] == ["A different episode's call"])


def test_rounds_are_measured_over_beats_the_card_finished_with():
    # The beat that never converged had 30 rounds and is still wrong. Sampling
    # it would make the projection rise the worse the work is going.
    progress = [{"number": 2, "node": "n", "total_beats": 3, "beats": [
        {"n": 1, "state": "done"}, {"n": 2, "state": "done"},
        {"n": 3, "state": "fix-known"}]}]
    scan = {"rounds": {("n", "1"): {"ltx": 2}, ("n", "2"): {"ltx": 4},
                       ("n", "3"): {"ltx": 30}}, "window": "", "jobs": 3}
    got = eta.rounds_medians(progress, scan)[0]
    check("median rounds skips the beat still in trouble", got["rounds_median"]["ltx"] == 3.0)
    check("and the sample size is the converged beats", got["finished_beats_sampled"] == 2)


def test_a_take_the_author_has_not_looked_at_yet_still_measures_the_card():
    # THE CORRECTION THAT MADE THIS FEATURE WORK. The card's job ends at a take
    # the author can look at; the yes is the other clock. Sampling `done` alone
    # would make the machine estimate depend on review speed and would report
    # "not estimable" for an episode the box has measurably spent days on —
    # which on 2026-08-13 was episode 2 exactly: nine rendered, zero passed.
    progress = [{"number": 2, "node": "n", "total_beats": 3, "beats": [
        {"n": 1, "state": "candidate-awaiting-founder"},
        {"n": 2, "state": "candidate-awaiting-founder"},
        {"n": 3, "state": "fix-known"}]}]
    scan = {"rounds": {("n", "1"): {"ltx": 3}, ("n", "2"): {"ltx": 5},
                       ("n", "3"): {"ltx": 30}}, "window": "", "jobs": 3}
    got = eta.rounds_medians(progress, scan)[0]
    check("an episode with nothing passed is still estimable",
          got["rounds_median"]["ltx"] == 4.0)
    check("both rendered beats are in the sample", got["finished_beats_sampled"] == 2)
    check("`done` is in the sampled set too", "done" in eta.MACHINE_FINISHED)
    check("a beat needing a re-render is not",
          not set(eta.MACHINE_FINISHED) & set(eta.NEEDS_RENDER))


def test_a_finished_beat_older_than_the_records_is_skipped_not_zeroed():
    # The sidecars start 2026-08-10. A beat finished before that has no rows —
    # which is "not recorded", not "took zero rounds". Averaging in a zero would
    # drag every remaining beat's estimate toward free.
    progress = [{"number": 1, "node": "n", "total_beats": 2, "beats": [
        {"n": 1, "state": "done"}, {"n": 2, "state": "done"}]}]
    scan = {"rounds": {("n", "2"): {"ltx": 6}}, "window": "", "jobs": 1}
    got = eta.rounds_medians(progress, scan)[0]
    check("the unrecorded beat is not a zero", got["rounds_median"]["ltx"] == 6.0)
    check("two beats are done, one is in the window",
          (got["machine_finished_beats"], got["finished_beats_sampled"]) == (2, 1))


def test_the_two_clocks_are_never_added():
    # Structural, not cosmetic: there is no field anywhere in a row that adds
    # machine time to decision time, because there is no number for the second.
    # If someone ever adds one, this test is where the argument gets had.
    with tempfile.TemporaryDirectory() as td:
        r = eta.rows(**_paths(Path(td)))[0]
    check("no row field claims a finish date",
          not any("date" in k or "finish_at" in k or "eta_at" in k for k in r))
    check("decisions are listed, not timed",
          all(set(d) == {"what", "url", "since"} for d in r["decisions"]))


def test_the_checked_in_states_are_well_formed():
    # The real file, not a fixture: every beat the repo claims a state for must
    # carry one this module defines, and the beat numbers must not collide.
    real = eta.read_progress()
    check("the repo's episode-progress.yaml parses to at least one episode", bool(real))
    for ep in real:
        tag = f"episode {ep.get('number')}"
        ns = [b["n"] for b in ep["beats"]]
        check(f"{tag}: no duplicate beat numbers", len(ns) == len(set(ns)))
        check(f"{tag}: beats are numbered 1..total_beats",
              sorted(ns) == list(range(1, int(ep["total_beats"]) + 1)))
        # EMITTED_STATES, not STATES: read_progress may DERIVE `stale-gate-closed`
        # from a blocked-decision whose gate has already opened. Widened here on
        # purpose and no wider — a typo'd state still fails this line.
        check(f"{tag}: every beat carries a defined state",
              all(b["state"] in eta.EMITTED_STATES for b in ep["beats"]))
        check(f"{tag}: it names where the states were read from",
              bool(ep["states_read_from"]))


def test_a_call_gets_a_name_not_a_sentence_cut_in_half():
    # Roman, 2026-08-13, on the first version: "im not seeing any eta ... except
    # this which isn't the best". Part of what made it unreadable was three
    # inbox paragraphs truncated at 90 characters into ellipsis soup. A label is
    # the headline clause, whole.
    import build_sim as bs
    cases = [
        ("Cold open fig - in both motion rounds the fig grows detached",
         "Cold open fig"),
        ("Beat 04 script length — faces survive 3s of motion, the beat is 6s",
         "Beat 04 script length"),
        ("EPISODE 2 - THE MORNING READ. Four beats look ready to cut",
         "EPISODE 2 - THE MORNING READ"),
    ]
    for what, want in cases:
        got = bs._call_label(what)
        check(f"“{want}” is the label", got == want)
    check("no label ends mid-ellipsis", "…" not in bs._call_label("x" * 200))
    check("a long unbroken title is cut on a word boundary",
          not bs._call_label("Beat 13 may be the first finished shot of the "
                             "whole of episode two").endswith(("-", " ")))
    check("empty text still names something", bs._call_label("") == "an open call")


def test_the_glance_cell_says_nothing_when_it_knows_nothing():
    # The strip must not grow a permanently apologetic sixth tile, and it must
    # never print a zero for a measurement it does not have.
    import build_sim as bs
    check("no rows → no cell at all", bs.eta_cell([]) == "")
    check("no rows (None) → no cell", bs.eta_cell(None) == "")
    row = {"number": 2, "machine_minutes": None, "needs_render": 3,
           "decisions": [], "ready": 0, "total": 21}
    out = bs.eta_cell([row])
    check("an unmeasured episode says 'not estimated'", "not estimated" in out)
    check("and never prints a zero", ">0<" not in out)
    row2 = dict(row, machine_minutes=222, decisions=[{}, {}, {}])
    out2 = bs.eta_cell([row2])
    check("a measured one leads with the hours", "about 3.7 h" in out2)
    check("names the episode", "episode 2" in out2)
    check("and counts the calls without timing them", "3 calls of it are yours" in out2)
    check("the cell is an anchor down to the card", 'href="#eta"' in out2)


def main() -> int:
    print("episode ETA — states, arithmetic, and what it refuses to claim")
    with tempfile.TemporaryDirectory() as td:
        test_every_beat_lands_in_exactly_one_state(Path(td))
        test_a_beat_waiting_on_the_author_is_not_work_for_the_card(Path(td))
        test_an_undecided_beat_is_costed_apart_from_the_certain_work(Path(td))
        test_a_missing_measurement_reads_as_unknown_and_never_as_zero(Path(td))
        test_an_absent_or_broken_progress_file_produces_no_row_at_all(Path(td))
        test_a_state_this_file_does_not_define_is_dropped_not_guessed(Path(td))
        test_a_thin_projection_says_so_and_still_prints(Path(td))
        test_the_gate_list_is_the_tagged_open_entries_and_says_what_it_missed(Path(td))
    test_rounds_are_measured_over_beats_the_card_finished_with()
    test_a_take_the_author_has_not_looked_at_yet_still_measures_the_card()
    test_a_finished_beat_older_than_the_records_is_skipped_not_zeroed()
    test_the_two_clocks_are_never_added()
    test_the_checked_in_states_are_well_formed()
    # THE CARD HE HAS TO BE ABLE TO READ, not just the numbers on it.
    test_a_call_gets_a_name_not_a_sentence_cut_in_half()
    test_the_glance_cell_says_nothing_when_it_knows_nothing()
    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} failure(s): {', '.join(FAILURES)}")
        return 1
    print("✓ all episode-ETA tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
