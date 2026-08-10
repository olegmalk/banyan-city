#!/usr/bin/env python3
"""Tests for the founder's phone channel: the published review surface and the answer log.

Two scripts, one job — the founder is away from the machine and both halves of
the loop have to work without him touching a terminal:

  * `pages_prefix.py`  re-bases the built site's root-absolute URLs so the
                       GitHub Pages mirror, which serves from a subpath, does not
                       404 every clip and sheet on the review page.
  * `poll_decisions.py` reads his replies off one issue and writes them down —
                       and, far more importantly, does not do anything else.

Pure functions and temp directories: no network, no `gh`, no build. Run:
    python3 pipeline/test_founder_channel.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pages_prefix as pp
import poll_decisions as pd

FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# pages_prefix — the review page must survive being served from a subpath
# ---------------------------------------------------------------------------
def test_root_absolute_media_is_rebased_onto_the_subpath():
    html = '<img src="/review/review-assets/LABELED-b01-r5.jpg">'
    out, n = pp.rebase_text(html, "/banyan-city")
    check("a root-absolute image gets the mirror's prefix",
          '"/banyan-city/review/review-assets/LABELED-b01-r5.jpg"' in out and n == 1)


def test_relative_and_external_refs_are_left_alone():
    html = ('<a href="../city.html">c</a><a href="https://x.test/a">x</a>'
            '<a href="#top">t</a><img src="//cdn.test/i.png">'
            '<img src="data:image/png;base64,AA">')
    out, n = pp.rebase_text(html, "/banyan-city")
    check("relative, external, fragment, protocol-relative and data refs untouched",
          out == html and n == 0)


def test_rebasing_twice_changes_nothing():
    # A workflow step gets retried; a retry must not produce /banyan-city/banyan-city/.
    html = '<img src="/review/x.jpg"><video poster="/review/p.png"></video>'
    once, n1 = pp.rebase_text(html, "/banyan-city")
    twice, n2 = pp.rebase_text(once, "/banyan-city")
    check("second pass is a no-op", once == twice and n1 == 2 and n2 == 0)


def test_a_prefix_that_is_only_a_string_match_is_not_a_subpath_match():
    # /banyan-cityscape must not read as already living under /banyan-city.
    out, n = pp.rebase_text('<img src="/banyan-cityscape/x.jpg">', "/banyan-city")
    check("prefix match is by path segment, not by characters",
          '"/banyan-city/banyan-cityscape/x.jpg"' in out and n == 1)


def test_the_prefix_is_normalised_however_it_is_written():
    check("bare name normalises", pp.normalise_prefix("banyan-city") == "/banyan-city")
    check("trailing slash normalises", pp.normalise_prefix("/banyan-city/") == "/banyan-city")
    check("root means no prefix", pp.normalise_prefix("/") == "")
    out, n = pp.rebase_text('<img src="/review/x.jpg">', "")
    check("an empty prefix is the identity", out == '<img src="/review/x.jpg">' and n == 0)


def test_css_url_references_are_rebased_too():
    out, n = pp.rebase_text('<style>a{background:url(/review/bg.png)}</style>', "/banyan-city")
    check("url() in a stylesheet is rebased", "url(/banyan-city/review/bg.png)" in out and n == 1)


def test_a_whole_tree_is_walked_and_dry_run_writes_nothing(tmp: Path):
    (tmp / "review").mkdir(parents=True)
    page = tmp / "review" / "index.html"
    page.write_text('<img src="/review/a.jpg"><img src="/review/b.jpg">', encoding="utf-8")
    before = page.read_text(encoding="utf-8")
    touched = pp.rebase_tree(tmp, "/banyan-city", dry_run=True)
    check("dry run reports the work", touched == [("review/index.html", 2)])
    check("dry run leaves the file alone", page.read_text(encoding="utf-8") == before)
    pp.rebase_tree(tmp, "/banyan-city", dry_run=False)
    check("a real run rewrites the file", "/banyan-city/review/a.jpg" in page.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# poll_decisions — the grammar
# ---------------------------------------------------------------------------
def test_the_short_forms_he_was_given_all_parse():
    recs = pd.parse_comment("20: yes")
    check("`20: yes` is a yes on the LTX card",
          len(recs) == 1 and recs[0]["intent"] == "yes"
          and recs[0]["card"] == "ltx-publish" and recs[0]["value"] is True)
    recs = pd.parse_comment("6: go")
    check("`6: go` releases the twelve frames",
          recs[0]["intent"] == "go" and recs[0]["card"] == "ep2-b01-r9")
    recs = pd.parse_comment("10: b06-r5-s2")
    check("`10: b06-r5-s2` is a frame pick",
          recs[0]["intent"] == "pick_frame" and recs[0]["frame"] == "b06-r5-s2"
          and recs[0]["beat"] == 6 and recs[0]["round"] == 5 and recs[0]["seed"] == 2)
    recs = pd.parse_comment("ep2: 002b-b18-r3-s0")
    check("an episode-qualified frame keeps its node",
          recs[0]["intent"] == "pick_frame" and recs[0]["node"] == "002b" and recs[0]["beat"] == 18)
    recs = pd.parse_comment("repo: olegmalk")
    check("`repo: olegmalk` is a note on the right card, not a verdict",
          recs[0]["intent"] == "note" and recs[0]["card"] == "repo-owner"
          and recs[0]["text"] == "olegmalk")


def test_a_number_answers_the_card_that_number_is_printed_on():
    # cuts.yaml's `n:` is what he sees; the list position is not. Confusing the
    # two would file his answer against a different question entirely.
    check("22 is the repo question", pd.resolve_key("22") == "repo-owner")
    check("11 is the crop question", pd.resolve_key("11") == "crop-704")
    check("an unknown number resolves to nothing", pd.resolve_key("99") is None)
    check("a slug resolves", pd.resolve_key("crop") == "crop-704")
    check("case and spacing do not matter", pd.resolve_key(" B06 ") == "ep1-beat06")


def test_several_answers_in_one_comment_are_all_recorded():
    recs = pd.parse_comment("20: yes\n11: no\n10: b06-r5-s2")
    check("three lines, three records", len(recs) == 3)
    check("they land on three different cards",
          {r["card"] for r in recs} == {"ltx-publish", "crop-704", "ep1-beat06"})
    check("the no is a no", [r for r in recs if r["card"] == "crop-704"][0]["value"] is False)


def test_a_quoted_question_is_not_read_as_its_own_answer():
    # Replying in the GitHub app quotes the thing you are replying to.
    recs = pd.parse_comment("> 20: LTX clips on the site — one yes or no.\n\n20: yes")
    check("the quote line is skipped", len(recs) == 1 and recs[0]["intent"] == "yes")


def test_a_bullet_or_numbered_list_still_parses():
    recs = pd.parse_comment("- 20: yes\n* 6: go\n1. 11: no")
    check("markdown list markers are stripped",
          [r["intent"] for r in recs] == ["yes", "go", "no"])


def test_anything_it_cannot_read_is_kept_verbatim_and_flagged():
    body = "not sure about the crop, let me look again tonight"
    recs = pd.parse_comment(body)
    check("a sentence is unparsed", recs[0]["intent"] == "unparsed")
    check("the sentence survives exactly", recs[0]["raw_line"] == body)
    recs = pd.parse_comment("99: yes")
    check("an unknown card number is unparsed, not guessed", recs[0]["intent"] == "unparsed")
    check("an empty comment still produces a record", pd.parse_comment("")[0]["intent"] == "unparsed")


def test_a_recognised_card_with_an_unrecognised_answer_becomes_a_note():
    recs = pd.parse_comment("19: the third shot still drags")
    check("his words stay attached to the right card",
          recs[0]["intent"] == "note" and recs[0]["card"] == "ep1-v34"
          and recs[0]["text"] == "the third shot still drags")


# ---------------------------------------------------------------------------
# poll_decisions — the log, and the boundary
# ---------------------------------------------------------------------------
def _comment(cid, body, author="olegmalk"):
    return {"id": cid, "body": body, "author": {"login": author},
            "createdAt": "2026-08-10T09:00:00Z"}


def test_a_comment_is_never_recorded_twice(tmp: Path):
    log = tmp / "founder-answers.jsonl"
    comments = [_comment("c1", "20: yes"), _comment("c2", "6: go")]
    first = pd.build_records(comments, pd.recorded_ids(log), 42)
    check("both comments are new the first time", len(first) == 2)
    log.write_text("".join(json.dumps(r) + "\n" for r in first), encoding="utf-8")
    second = pd.build_records(comments, pd.recorded_ids(log), 42)
    check("nothing is new the second time", second == [])
    third = pd.build_records(comments + [_comment("c3", "11: no")], pd.recorded_ids(log), 42)
    check("only the genuinely new comment is picked up",
          len(third) == 1 and third[0]["card"] == "crop-704")


def test_the_log_is_the_watermark_so_losing_the_state_file_costs_nothing(tmp: Path):
    log = tmp / "a.jsonl"
    recs = pd.build_records([_comment("c1", "20: yes")], set(), 42)
    log.write_text(json.dumps(recs[0]) + "\n", encoding="utf-8")
    # no state file exists at all here — dedupe must still hold
    check("dedupe works with no state file",
          pd.build_records([_comment("c1", "20: yes")], pd.recorded_ids(log), 42) == [])


def test_one_unreadable_line_does_not_blind_the_whole_log(tmp: Path):
    log = tmp / "a.jsonl"
    log.write_text('{"comment_id": "c1"}\nnot json at all\n{"comment_id": "c2"}\n', encoding="utf-8")
    ids = pd.recorded_ids(log)
    check("the readable ids are still found", ids == {"c1", "c2"})


def test_every_record_carries_its_provenance(tmp: Path):
    recs = pd.build_records([_comment("c9", "20: yes")], set(), 42)
    r = recs[0]
    check("the comment id is on the record", r["comment_id"] == "c9")
    check("the raw comment is preserved whole", r["raw"] == "20: yes")
    check("the author and timestamps are there",
          r["author"] == "olegmalk" and r["created_at"] == "2026-08-10T09:00:00Z" and r["recorded_at"])
    check("the issue is named", r["issue"] == 42)


def test_the_poller_has_no_way_to_act_on_an_answer():
    # The guarantee this whole file exists for. If someone ever adds a call that
    # renders, promotes or spends, this is the test that should stop them.
    src = (Path(__file__).resolve().parent / "poll_decisions.py").read_text(encoding="utf-8")
    body = src.split('"""', 2)[2]          # skip the module docstring, which discusses them
    forbidden = ["render_t3", "render_local", "generate_shots", "ltx_i2v",
                 "git commit", "git push", "shutil.copy", "os.replace", "--yes"]
    hits = [f for f in forbidden if f in body]
    check("it calls nothing that renders, promotes, commits or spends", hits == [])
    check("the only subprocess it runs is a read from gh",
          body.count("subprocess.run") == 1 and 'cmd = ["gh", "issue", "view"' in body)


def main():
    print("founder phone channel — review surface + answer log\n")
    print("pages_prefix — the mirror's subpath")
    test_root_absolute_media_is_rebased_onto_the_subpath()
    test_relative_and_external_refs_are_left_alone()
    test_rebasing_twice_changes_nothing()
    test_a_prefix_that_is_only_a_string_match_is_not_a_subpath_match()
    test_the_prefix_is_normalised_however_it_is_written()
    test_css_url_references_are_rebased_too()
    with tempfile.TemporaryDirectory() as td:
        test_a_whole_tree_is_walked_and_dry_run_writes_nothing(Path(td))

    print("\npoll_decisions — the grammar")
    test_the_short_forms_he_was_given_all_parse()
    test_a_number_answers_the_card_that_number_is_printed_on()
    test_several_answers_in_one_comment_are_all_recorded()
    test_a_quoted_question_is_not_read_as_its_own_answer()
    test_a_bullet_or_numbered_list_still_parses()
    test_anything_it_cannot_read_is_kept_verbatim_and_flagged()
    test_a_recognised_card_with_an_unrecognised_answer_becomes_a_note()

    print("\npoll_decisions — the log, and the boundary")
    with tempfile.TemporaryDirectory() as td:
        test_a_comment_is_never_recorded_twice(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_the_log_is_the_watermark_so_losing_the_state_file_costs_nothing(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_one_unreadable_line_does_not_blind_the_whole_log(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_every_record_carries_its_provenance(Path(td))
    test_the_poller_has_no_way_to_act_on_an_answer()

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} failure(s): {', '.join(FAILURES)}")
        return 1
    print("✓ all founder-channel tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
