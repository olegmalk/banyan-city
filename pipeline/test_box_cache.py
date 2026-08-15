#!/usr/bin/env python3
"""Tests for pipeline/box_cache.py — the tool that deletes render media.

Every case here is about the same asymmetry. Keeping a file that could have
been dropped costs disk. Dropping a file that had no other copy destroys work
that took GPU-hours, and destroys it silently, because nothing on this laptop
would notice until someone opened the page it was for.

So the decision function is pure and is tested directly, with no box, no ssh
and no real filesystem: the guards are the product, and they have to be
readable as a list of sentences a person can check.

Context, 2026-08-11: the Mac hit 9.6 GiB free — down from 19 GiB two hours
earlier — while the render box sat on 217 GB, because everything rendered on
the box was fetched here and kept. That is what the tool is for, and it is
also exactly the mood in which someone reaches for a delete loop and skips
the proving step.

Run: python3 pipeline/test_box_cache.py
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import box_cache as bc

FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


def f(rel, size=1000, sha="a" * 64):
    return bc.LocalFile(rel, size, sha)


def verdict_for(files, remote=None, tracked=(), referenced=()):
    out = bc.classify(files, remote or {}, set(tracked), set(referenced))
    return {v.rel: v for v in out}


def test_a_file_with_a_verified_twin_is_reclaimable():
    """The whole point: bytes proven to exist on the box may leave the Mac."""
    v = verdict_for([f("review/tonight/02-three-oh-seven.mp4", sha="b" * 64)],
                    remote={"b" * 64: ["C:\\banyan-farm\\out\\02.mp4"]})
    got = v["review/tonight/02-three-oh-seven.mp4"]
    check("a byte-identical box copy makes a clip reclaimable",
          got.action == "reclaim")
    check("the verdict records WHICH box file proved it, for the fetch back",
          got.box_path == "C:\\banyan-farm\\out\\02.mp4")


def test_a_file_with_no_twin_is_never_reclaimed():
    """The five 2026-08-06 MPS repaints existed nowhere but this laptop."""
    v = verdict_for([f("genomes/sapling/nodes/002b/takes/stills/01-a.png",
                       sha="c" * 64)],
                    remote={"d" * 64: ["C:\\banyan-farm\\other.png"]})
    got = v["genomes/sapling/nodes/002b/takes/stills/01-a.png"]
    check("a file the box has never seen is kept", got.action == "keep")
    check("and the report says why in plain words",
          "no byte-identical copy" in got.why)


def test_a_same_name_different_bytes_file_is_not_a_twin():
    """Farm filenames collide constantly — three tasks for one beat all
    normalise to the same name (the bug collect_farm.py exists to fix). A
    name match here would delete the good take because a stale one shares
    its title, so matching is on sha256 and only sha256."""
    v = verdict_for([f("review/tonight/01-the-keyboard.mp4", sha="e" * 64)],
                    remote={"f" * 64: ["C:\\banyan-farm\\01-the-keyboard.mp4"]})
    check("same filename, different bytes, still kept",
          v["review/tonight/01-the-keyboard.mp4"].action == "keep")


def test_a_tracked_file_is_never_reclaimed():
    """001's takes/ archive is committed on purpose. Tracked media's home is
    the repo; having a copy on the box is not a reason to remove it."""
    rel = "genomes/sapling/nodes/001-capability-inventory/takes/archive/01.png"
    v = verdict_for([f(rel, sha="1" * 64)],
                    remote={"1" * 64: ["C:\\banyan-farm\\01.png"]},
                    tracked={rel})
    check("a git-tracked file is kept even with a verified twin",
          v[rel].action == "keep")
    check("and the reason names git", "tracked in git" == v[rel].why)


def test_a_page_referenced_file_is_never_reclaimed():
    """A committed page pointing at a file expects that file on disk. The
    ignore rules say nothing about that, so it is checked separately."""
    rel = "review/tonight/07-zero-0-moving-parts-LTX-385f.mp4"
    v = verdict_for([f(rel, sha="2" * 64)],
                    remote={"2" * 64: ["C:\\banyan-farm\\07.mp4"]},
                    referenced={"07-zero-0-moving-parts-LTX-385f.mp4"})
    check("a file a committed page names is kept",
          v[rel].action == "keep")
    check("and the reason names the page, not the ignore rule",
          "committed page" in v[rel].why)


def test_reference_scan_finds_names_in_html_and_markdown_alike():
    names = bc.referenced_names([
        '<video src="clips/04-the-fall.mp4" poster="04.png"></video>',
        "| beat 6 | `06-too-blue-LTX-121f.mp4` | held |",
        "audio: 03-vo.mp3\n",
    ])
    check("html src, a markdown table cell and a yaml value all count",
          names == {"04-the-fall.mp4", "04.png",
                    "06-too-blue-LTX-121f.mp4", "03-vo.mp3"})


def test_a_file_a_lane_just_wrote_is_kept():
    """This is a shared worktree. On 2026-08-11 a lane was rebuilding the cut
    in review/tonight/ while this tool was being written. A file mid-arrival
    can already be byte-identical to its box original and still be something a
    running job is about to open."""
    fresh = bc.LocalFile("review/tonight/03-fresh.mp4", 900, "4" * 64, age_s=60)
    old = bc.LocalFile("review/tonight/03-old.mp4", 900, "4" * 64, age_s=99999)
    v = {x.rel: x for x in bc.classify([fresh, old], {"4" * 64: ["C:\\a.mp4"]},
                                       set(), set())}
    check("a file written a minute ago is left alone",
          v["review/tonight/03-fresh.mp4"].action == "keep")
    check("and the reason names the lane, not the box",
          "lane" in v["review/tonight/03-fresh.mp4"].why)
    check("the same bytes, older, are still reclaimable",
          v["review/tonight/03-old.mp4"].action == "reclaim")


def test_an_empty_file_is_kept():
    """A zero-byte file hashes to a constant every other zero-byte file on the
    box shares, so 'verified' would be meaningless. It also frees nothing."""
    v = verdict_for([f("review/tonight/truncated.mp4", size=0, sha="3" * 64)],
                    remote={"3" * 64: ["C:\\banyan-farm\\empty.mp4"]})
    check("an empty file is never counted as proven",
          v["review/tonight/truncated.mp4"].action == "keep")


def test_only_review_and_takes_media_are_ever_candidates():
    check("a review clip qualifies",
          bc.is_candidate("review/tonight/02.mp4"))
    check("a node's takes/ candidate qualifies",
          bc.is_candidate("genomes/sapling/nodes/002b/takes/stills/01.png"))
    check("a published leaf does NOT — it is the work, not a cache copy",
          not bc.is_candidate(
              "genomes/sapling/nodes/006a/leaves/006a-t3-b.mp4"))
    check("a provenance sidecar beside a clip is never touched",
          not bc.is_candidate("review/tonight/02.mp4.meta.yaml"))
    check("the built site is not this tool's business",
          not bc.is_candidate("_site/sapling/leaves/006a-t3-b.mp4"))


def test_an_unreachable_box_proves_nothing_and_drops_nothing():
    """classify() with an empty remote index is the state a failed ssh leaves.
    Every file must survive it — the callers additionally refuse to delete at
    all in that case, but the decision layer has to be safe on its own."""
    files = [f(f"review/tonight/{i:02d}.mp4", sha=str(i) * 64) for i in range(5)]
    v = bc.classify(files, {}, set(), set())
    check("no remote index means no reclaims", all(x.action == "keep" for x in v))


def test_the_remote_script_hashes_only_size_matched_files():
    """Hashing all 35,416 files on the box to answer a question about 900
    would take longer than the renders it interrupts."""
    s = bc.remote_hash_script([1211565, 4096, 4096], ["C:\\banyan-farm"])
    check("every distinct local size is in the filter",
          '"1211565"=1' in s and '"4096"=1' in s)
    check("sizes are deduplicated", s.count('"4096"=1') == 1)
    check("the filter runs BEFORE Get-FileHash",
          s.index("ContainsKey") < s.index("Get-FileHash"))
    check("size keys are strings — an Int32 literal never matches an Int64 "
          "Length, and ContainsKey fails silently across the two",
          '$_.Length.ToString()' in s)
    check("the box's own free space rides home on the same round trip",
          "#FREE" in s)


def test_parsing_the_box_reply_ignores_noise():
    out = ("#FREE\t233000000000\r\n"
           "AB" + "0" * 62 + "\t123\tC:\\banyan-farm\\a.png\r\n"
           "warning: something scrolled past\r\n"
           "AB" + "0" * 62 + "\t123\tC:\\banyan-farm\\dup\\a.png\r\n")
    remote, free = bc.parse_remote(out)
    check("free space is read off the box", free == 233000000000)
    check("shas are lowercased so local and remote compare",
          list(remote) == ["ab" + "0" * 62])
    check("both box copies are remembered", len(remote["ab" + "0" * 62]) == 2)
    check("a line that is not a hash row is dropped, not guessed at",
          all(len(k) == 64 for k in remote))


def test_a_page_names_its_own_subset():
    """Fetch-on-demand: the page declares what it needs and only that comes
    back over the wire."""
    refs = bc.page_media_refs(
        '<video src="02-three-oh-seven.mp4" poster="02.png"></video>'
        '<a href="clips/04-the-fall.mp4">fall</a>'
        '<a href="notes.md">notes</a>'
        '<video src="02-three-oh-seven.mp4"></video>')
    check("media the page embeds is listed once, in order",
          refs == ["02-three-oh-seven.mp4", "02.png", "clips/04-the-fall.mp4"])


def test_the_disk_reading_carries_a_date_and_the_warn_line():
    doc = bc.disk_reading(box_free=217 * 1024 ** 3, cached=1234, reclaimable=99)
    for key in ("measured_on:", "free_bytes:", "total_bytes:",
                "warn_below_bytes:", "cached_media_bytes:",
                "reclaimable_bytes:", "box_free_bytes:", "box_checked_on:"):
        check(f"the reading carries {key}", key in doc)
    check("it never publishes a number without saying when it was taken",
          doc.index("measured_on:") < doc.index("free_bytes:"))


def test_a_reading_taken_without_the_box_claims_nothing_about_the_box():
    """`disk` runs on every screening-gate pass and never touches the box. It
    must not therefore publish a reclaimable total of zero, which would read as
    'nothing here is backed up' — the exact false negative this whole tool is
    built to avoid printing."""
    doc = bc.disk_reading(cached=1234)
    check("no box figure means no box rows at all",
          "box_free_bytes:" not in doc and "reclaimable_bytes:" not in doc)
    check("the local figures are still there", "free_bytes:" in doc)


def test_the_previous_reading_round_trips():
    """The carry-forward that lets a cheap `disk` run keep the expensive box
    figures, under their own older date rather than a fresh one."""
    doc = bc.disk_reading(box_free=99, cached=5, reclaimable=7,
                          box_checked_on="2026-08-11T09:00:00")
    flat = {}
    for line in doc.splitlines():
        if not line.startswith("#") and ":" in line:
            k, v = line.split(":", 1)
            flat[k.strip()] = v.strip()
    check("the box figures survive as written",
          flat["box_free_bytes"] == "99" and flat["reclaimable_bytes"] == "7")
    check("and keep the date they were actually taken on",
          flat["box_checked_on"] == "2026-08-11T09:00:00")


# ------------------------------------------------ the git repack litter sweep
#
# Same asymmetry as everything above, one directory over. Leaving a dead
# tmp_pack_* costs 350 MB; removing a live repack's working file corrupts the
# operation, and removing anything else in .git/objects/pack destroys history.
# So the two conditions — the tmp_pack_ prefix and the one-hour age — are tested
# as the product they are.


HOUR = 3600.0


def _pack_dir(files, tmp):
    """A fake .git/objects/pack. `files` = {name: age_in_seconds}."""
    d = Path(tmp) / "pack"
    d.mkdir()
    now = 1_700_000_000.0
    for name, age in files.items():
        p = d / name
        p.write_bytes(b"x" * 100)
        os.utime(p, (now - age, now - age))
    return d, now


def _counts(garbage=2, in_pack=5):
    return lambda: {"garbage": garbage, "in-pack": in_pack, "count": 3}


def test_a_tmp_pack_younger_than_an_hour_is_never_removed():
    """It may be the working file of a repack running RIGHT NOW.

    A dozen lanes commit into this worktree, so `git gc --auto` fires often and
    a repack usually IS in flight. Unlinking its temp file corrupts it.
    """
    check("a 5-minute-old tmp_pack is left alone",
          bc.stale_tmp_packs([("tmp_pack_abc", 0.0)], now=300.0) == [])
    check("59 minutes is still too young",
          bc.stale_tmp_packs([("tmp_pack_abc", 0.0)], now=59 * 60.0) == [])
    check("an hour old is wreckage and goes",
          bc.stale_tmp_packs([("tmp_pack_abc", 0.0)], now=HOUR)
          == ["tmp_pack_abc"])

    with tempfile.TemporaryDirectory() as tmp:
        d, now = _pack_dir({"tmp_pack_young": 60, "tmp_pack_old": 3 * HOUR}, tmp)
        got = bc.sweep_git_tmp_packs(pack_dir=d, now=now, counts=_counts(),
                                     log=lambda *a: None)
        check("the sweep unlinks only the old one",
              got["removed"] == ["tmp_pack_old"])
        check("and the young one is still on disk",
              (d / "tmp_pack_young").exists())
        check("freed bytes are counted from the file that actually went",
              got["freed"] == 100)


def test_nothing_but_a_tmp_pack_is_ever_touched():
    """A wrong glob here does not waste disk — it destroys the repository."""
    others = [("pack-9c1.pack", 0.0), ("pack-9c1.idx", 0.0),
              ("pack-9c1.rev", 0.0), ("pack-9c1.mtimes", 0.0),
              ("tmp_idx_991", 0.0), ("multi-pack-index", 0.0)]
    check("real packs, idx, rev, mtimes and the midx all survive, however old",
          bc.stale_tmp_packs(others, now=90 * 24 * HOUR) == [])

    with tempfile.TemporaryDirectory() as tmp:
        names = {"pack-9c1.pack": 9 * HOUR, "pack-9c1.idx": 9 * HOUR,
                 "tmp_pack_dead": 9 * HOUR}
        d, now = _pack_dir(names, tmp)
        got = bc.sweep_git_tmp_packs(pack_dir=d, now=now, counts=_counts(),
                                     log=lambda *a: None)
        check("only the tmp_pack_ file is unlinked",
              got["removed"] == ["tmp_pack_dead"])
        check("the real pack is still there", (d / "pack-9c1.pack").exists())
        check("and so is its index", (d / "pack-9c1.idx").exists())


def test_the_sweep_reports_garbage_and_in_pack_on_both_sides():
    """in-pack is the number that proves wreckage went and history did not."""
    with tempfile.TemporaryDirectory() as tmp:
        d, now = _pack_dir({"tmp_pack_dead": 9 * HOUR}, tmp)
        seen = iter([{"garbage": 1, "in-pack": 38710},
                     {"garbage": 0, "in-pack": 38710}])
        got = bc.sweep_git_tmp_packs(pack_dir=d, now=now,
                                     counts=lambda: next(seen),
                                     log=lambda *a: None)
        check("the before reading is returned", got["before"]["garbage"] == 1)
        check("the after reading is returned", got["after"]["garbage"] == 0)
        check("in-pack is reported on both sides and unchanged",
              got["before"]["in-pack"] == got["after"]["in-pack"] == 38710)

    with tempfile.TemporaryDirectory() as tmp:
        d, now = _pack_dir({"tmp_pack_dead": 9 * HOUR}, tmp)
        seen = iter([{"garbage": 1, "in-pack": 38710},
                     {"garbage": 0, "in-pack": 12}])
        said = []
        bc.sweep_git_tmp_packs(pack_dir=d, now=now, counts=lambda: next(seen),
                               log=said.append)
        check("an in-pack that moved is called out, not reported as success",
              any("in-pack CHANGED" in s for s in said))


def test_a_broken_or_absent_git_never_stops_the_caller():
    """This runs at the top of an encode. It may cost disk; it may not cost a render."""
    def explode():
        raise FileNotFoundError("git")

    said = []
    got = bc.sweep_git_tmp_packs(counts=explode, log=said.append)
    check("git missing = empty result, no exception", got == {})
    check("and it says why", any("skipped" in s for s in said))

    got = bc.sweep_git_tmp_packs(counts=lambda: {}, log=lambda *a: None)
    check("a git that answered nothing deletes nothing", got["removed"] == [])

    got = bc.sweep_git_tmp_packs(pack_dir="/nope/not/here", now=0.0,
                                 counts=_counts(), log=lambda *a: None)
    check("a pack dir that is not there is not an error either", got == {})

    got = bc.sweep_git_tmp_packs(counts=_counts(garbage=0),
                                 log=lambda *a: None)
    check("git reporting no garbage means the dir is not even opened",
          got["removed"] == [] and got["freed"] == 0)


# ------------------------------------------------- stale scratchpad worktrees
#
# Each of the four conditions in prunable_worktrees gets a test that turns off
# THAT ONE and leaves the rest good, because the failure being guarded against
# is a condition quietly going missing. A worktree that is fine on three counts
# and wrong on the fourth must still survive.

DAY = 24 * 60 * 60


def _wt(path="/private/tmp/claude-501/s/pub", newest=0.0, dirty=0,
        on_origin=True, in_scratch=True):
    """A worktree that is prunable, so a test can spoil exactly one thing."""
    return bc.WorktreeState(path, newest, dirty, on_origin, in_scratch)


def test_a_worktree_outside_the_scratchpad_is_never_prunable():
    # The main checkout and the farm clones are worktrees too. This is the only
    # thing standing between the sweep and somebody's real tree.
    check("a clean, pushed, ancient worktree outside the scratchpad stays",
          bc.prunable_worktrees([_wt(in_scratch=False)], now=DAY) == [])


def test_a_worktree_with_uncommitted_or_ignored_files_stays():
    # dirty counts `--porcelain --ignored`, so one un-pushed render output is
    # enough to save the tree — that clip is the only copy of itself.
    check("one dirty/ignored file keeps the whole worktree",
          bc.prunable_worktrees([_wt(dirty=1)], now=DAY) == [])


def test_a_worktree_off_origin_main_stays():
    # Clean but unpushed: the commit exists nowhere else, so this checkout is
    # the only copy of that arrangement of the tree.
    check("a clean worktree on an unpushed commit is kept",
          bc.prunable_worktrees([_wt(on_origin=False)], now=DAY) == [])


def test_a_recently_touched_worktree_stays():
    check("a worktree touched an hour ago is a live lane's",
          bc.prunable_worktrees([_wt(newest=DAY - 3600)], now=DAY) == [])
    check("eleven hours is still too young",
          bc.prunable_worktrees([_wt(newest=0.0)], now=11 * 3600) == [])


def test_a_stale_clean_pushed_scratch_worktree_goes():
    check("twelve hours old, clean, pushed and in the scratchpad — removable",
          bc.prunable_worktrees([_wt()], now=12 * 3600)
          == ["/private/tmp/claude-501/s/pub"])


def test_newest_mtime_sees_a_file_a_stale_directory_hides():
    # The bug this exists to prevent, measured 2026-08-15: two session
    # directories whose OWN mtime read days old held files written that evening.
    # Reading the directory would have deleted a running lane's tree.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        deep = root / "a" / "b"
        deep.mkdir(parents=True)
        fresh = deep / "lane-is-working.txt"
        fresh.write_text("x")
        os.utime(fresh, (2_000_000_000, 2_000_000_000))
        os.utime(root, (1_000_000, 1_000_000))      # directory looks ancient
        check("the directory's own mtime is old",
              root.stat().st_mtime < 2_000_000)
        check("newest_mtime finds the fresh file buried under it",
              bc.newest_mtime(root) == 2_000_000_000)


def test_the_worktree_sweep_defaults_to_deleting_nothing():
    # A sweep that reports too much costs a gigabyte; one that deletes too much
    # costs a night of unattended rendering. So dry_run is the default.
    said = []
    got = bc.sweep_stale_worktrees(scan=lambda: [_wt(newest=0.0)],
                                   now=DAY, log=said.append)
    check("the default run is a dry run", got["dry_run"] is True)
    check("it says WOULD rather than claiming it removed anything",
          any("WOULD remove" in s for s in said))
    check("nothing was actually removed by a default call",
          not any("worktree removed:" in s for s in said))


def main() -> int:
    for fn in [
        test_a_file_with_a_verified_twin_is_reclaimable,
        test_a_file_with_no_twin_is_never_reclaimed,
        test_a_same_name_different_bytes_file_is_not_a_twin,
        test_a_tracked_file_is_never_reclaimed,
        test_a_page_referenced_file_is_never_reclaimed,
        test_reference_scan_finds_names_in_html_and_markdown_alike,
        test_a_file_a_lane_just_wrote_is_kept,
        test_an_empty_file_is_kept,
        test_only_review_and_takes_media_are_ever_candidates,
        test_an_unreachable_box_proves_nothing_and_drops_nothing,
        test_the_remote_script_hashes_only_size_matched_files,
        test_parsing_the_box_reply_ignores_noise,
        test_a_page_names_its_own_subset,
        test_the_disk_reading_carries_a_date_and_the_warn_line,
        test_a_reading_taken_without_the_box_claims_nothing_about_the_box,
        test_the_previous_reading_round_trips,
        test_a_tmp_pack_younger_than_an_hour_is_never_removed,
        test_nothing_but_a_tmp_pack_is_ever_touched,
        test_the_sweep_reports_garbage_and_in_pack_on_both_sides,
        test_a_broken_or_absent_git_never_stops_the_caller,
        test_a_worktree_outside_the_scratchpad_is_never_prunable,
        test_a_worktree_with_uncommitted_or_ignored_files_stays,
        test_a_worktree_off_origin_main_stays,
        test_a_recently_touched_worktree_stays,
        test_a_stale_clean_pushed_scratch_worktree_goes,
        test_newest_mtime_sees_a_file_a_stale_directory_hides,
        test_the_worktree_sweep_defaults_to_deleting_nothing,
    ]:
        print(fn.__name__)
        fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED: " + ", ".join(FAILURES))
        return 1
    print("all box_cache tests pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
