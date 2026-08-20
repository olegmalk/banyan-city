#!/usr/bin/env python3
"""The build-commit stamp, both ends of it — written, then read back.

WHY THIS FILE EXISTS. The freshness check in qa_local.py was BLIND before this
stamp: it read the deploy's age off Vercel's `last-modified`, which is a CDN
cache-fill instant, so it could not tell a current deploy from one frozen for
36 hours and printed green through both. The stamp is the repair — the build
states its own commit in the bytes it writes.

Which means the failure mode this file guards is not "the stamp is wrong". It
is **the stamp being absent, unreadable or a lie, and the check reading that as
current anyway** — turning a blind check into a falsely green one, which is
strictly worse than what we had. So most of the cases below are about the
non-answers: no tag, `unknown`, garbage, and a build from a dirty tree whose
bytes were never in any commit. Every one of them must come back as a warn that
says UNKNOWN, and not one of them may come back "ok".

No network and no git: build_commit's git access is injected, and the reader is
handed HTML strings. Run: python3 pipeline/test_build_stamp.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_commit as bc  # noqa: E402
import qa_local as qa  # noqa: E402

HEAD40 = "15ee724aabbccddeeff00112233445566778899a"
HEAD7 = HEAD40[:7]
OLD7 = "aef79ac"

FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


def fake_git(sha=HEAD40, dirty=False, ct="1786427284", status=None):
    """A stand-in for build_commit._git. Returns "" for a command it does not
    know, which is exactly how the real one reports failure — so a branch that
    forgets to handle "" shows up here rather than in production.

    `status` is the raw porcelain block when a case needs to say WHICH kind of
    change it means — `??` untracked and ` M` tracked are weighted differently
    in a platform checkout. `dirty=True` is the shorthand for one tracked edit.
    """
    porcelain = status
    if porcelain is None:
        porcelain = " M pipeline/build_site.py" if dirty else ""

    def run(args):
        if args[:2] == ["rev-parse", "HEAD"]:
            return sha
        if args[:2] == ["status", "--porcelain"]:
            return porcelain
        if args[:2] == ["log", "-1"]:
            return ct
        return ""
    return run


# What the Vercel build container leaves in /vercel/path0 beside the checkout:
# untracked, ours by neither authorship nor .gitignore.
CONTAINER_DROPPINGS = "?? .cache/\n?? .npm/\n"


def head(*metas):
    """The smallest page shaped like the ones the builders emit."""
    return "<!doctype html><html><head>" + "".join(metas) + "</head><body>x</body></html>"


STAMP = '<meta name="build-commit" content="%s">'
STAMP_T = '<meta name="build-commit-time" content="%s">'


# ---------------------------------------------------------------- the writer


def test_a_clean_checkout_stamps_the_commit_it_is_sitting_on():
    info = bc.build_commit(env={}, git=fake_git())
    check("clean tree → short sha of HEAD", info["sha"] == HEAD7)
    check("clean tree → not dirty", info["dirty"] is False)
    check("clean tree → the commit's own time", info["commit_time"] == 1786427284)
    check("clean tree → stamps a bare sha", bc.stamp_value(info) == HEAD7)


def test_a_build_from_an_uncommitted_tree_refuses_to_claim_a_clean_sha():
    # The bytes being built were never in any commit, so naming the commit the
    # tree happens to sit on would be the precise lie the stamp exists to stop.
    # `-dirty` is git-describe's spelling and cannot be read as a sha.
    info = bc.build_commit(env={}, git=fake_git(dirty=True))
    check("dirty tree → flagged dirty", info["dirty"] is True)
    check("dirty tree → sha carries -dirty", bc.stamp_value(info) == HEAD7 + "-dirty")
    check("dirty stamp is not a bare sha", bc.stamp_value(info) != HEAD7)


def test_a_build_that_cannot_see_git_falls_back_to_what_the_platform_says():
    # Vercel and Actions both name the sha they checked out. A checkout of a
    # named sha is clean by construction; its commit TIME is not on offer, and
    # is left None rather than guessed at with "now".
    no_git = fake_git(sha="")
    v = bc.build_commit(env={"VERCEL_GIT_COMMIT_SHA": HEAD40.upper()}, git=no_git)
    check("VERCEL_GIT_COMMIT_SHA is used when git is unavailable", v["sha"] == HEAD7)
    check("a platform sha is not marked dirty", v["dirty"] is False)
    check("a platform sha carries no invented time", v["commit_time"] is None)
    g = bc.build_commit(env={"GITHUB_SHA": HEAD40}, git=no_git)
    check("GITHUB_SHA is used too (the Pages mirror)", g["sha"] == HEAD7)


def test_a_container_dropping_beside_a_platform_checkout_is_not_an_uncommitted_build():
    # THE 2026-08-20 CASE. Every banyan.city production deploy stamped
    # `<sha>-dirty`, which is a flag that is always on and therefore says
    # nothing: qa_local could never call the live site current. Nothing in the
    # repo did it — the Pages mirror builds the same generator on Linux and
    # stamps clean, and so does a full `vercel build` over a pristine clone —
    # so what is left in the tree is the Vercel build container's, arriving
    # after a checkout the platform itself named.
    env = {"VERCEL_GIT_COMMIT_SHA": HEAD40}
    info = bc.build_commit(env=env, git=fake_git(status=CONTAINER_DROPPINGS))
    check("platform checkout + untracked droppings → not dirty",
          info["dirty"] is False)
    check("platform checkout stamps the bare sha", bc.stamp_value(info) == HEAD7)
    check("the droppings are still recorded, not discarded",
          len(info["entries"]) == 2)
    check("the exempting checkout names itself",
          info["checkout"] == "VERCEL_GIT_COMMIT_SHA")
    check("git still supplies the commit time a platform sha cannot",
          info["commit_time"] == 1786427284)


def test_a_tracked_edit_is_dirty_even_in_a_platform_checkout():
    # The exemption is for files git is not following. A MODIFIED tracked file
    # means the bytes being built are not the commit's bytes, which is the one
    # thing `-dirty` exists to say, and no environment excuses it.
    env = {"VERCEL_GIT_COMMIT_SHA": HEAD40}
    both = CONTAINER_DROPPINGS + " M genomes/sapling/lineage.yaml\n"
    info = bc.build_commit(env=env, git=fake_git(status=both))
    check("platform checkout + a tracked edit → dirty", info["dirty"] is True)
    check("that stamp carries -dirty", bc.stamp_value(info) == HEAD7 + "-dirty")
    info = bc.build_commit(env=env, git=fake_git(status=" D cuts/cuts.yaml\n"))
    check("a deleted tracked file is dirty too", info["dirty"] is True)


def test_the_exemption_needs_the_platform_and_git_to_agree_on_the_commit():
    # A platform variable naming some OTHER commit means the checkout is not
    # what the platform thinks it is. That is exactly when to stay strict, so
    # the exemption is keyed on agreement, never on the variable being set.
    other = "aef79ac1122334455667788990011223344556677"
    info = bc.build_commit(env={"VERCEL_GIT_COMMIT_SHA": other},
                           git=fake_git(status=CONTAINER_DROPPINGS))
    check("platform sha ≠ HEAD → no exemption", info["dirty"] is True)
    check("platform sha ≠ HEAD → no checkout claimed", info["checkout"] is None)
    # A short sha from a platform that abbreviates still matches by prefix.
    short = bc.build_commit(env={"VERCEL_GIT_COMMIT_SHA": HEAD7},
                            git=fake_git(status=CONTAINER_DROPPINGS))
    check("an abbreviated platform sha still matches HEAD", short["dirty"] is False)


def test_an_untracked_file_on_a_developers_machine_still_dirties_the_build():
    # No platform variable, no exemption. The builder reads media out of the
    # tree and can publish a file that was never committed, which is why
    # --porcelain (not `diff --quiet`) was chosen here in the first place.
    info = bc.build_commit(env={}, git=fake_git(status=CONTAINER_DROPPINGS))
    check("untracked, no platform → dirty", info["dirty"] is True)
    check("untracked, no platform → -dirty stamp",
          bc.stamp_value(info) == HEAD7 + "-dirty")


def test_a_dirty_build_names_the_paths_that_made_it_dirty():
    # The whole cost of the 2026-08-20 bug was that `-dirty` named nothing, so
    # three sessions could only guess what the container leaves behind.
    import io
    buf = io.StringIO()
    bc._report(bc.build_commit(env={}, git=fake_git(status=CONTAINER_DROPPINGS)), buf)
    out = buf.getvalue()
    check("the report names a path", ".npm/" in out)
    check("the report says which stamp it explains", HEAD7 + "-dirty" in out)
    quiet = io.StringIO()
    bc._report(bc.build_commit(env={}, git=fake_git()), quiet)
    check("a clean tree reports nothing at all", quiet.getvalue() == "")
    # Exempted droppings are reported too — swallowed silently is how a real
    # cause hides behind a rule written for a fake one.
    ci = io.StringIO()
    bc._report(bc.build_commit(env={"VERCEL_GIT_COMMIT_SHA": HEAD40},
                               git=fake_git(status=CONTAINER_DROPPINGS)), ci)
    check("an exempted dropping is still printed", ".cache/" in ci.getvalue())
    check("the exempt report says it was not counted",
          "not counted" in ci.getvalue())


def test_a_build_that_knows_nothing_says_unknown_rather_than_nothing():
    # Absent and unknown are different facts with different fixes — an old
    # deploy versus a build environment that cannot read its checkout — so the
    # builder must not be able to produce the absent case by shrugging.
    info = bc.build_commit(env={}, git=fake_git(sha=""))
    check("no git, no platform → empty sha", info["sha"] == "")
    check("no git, no platform → stamps `unknown`", bc.stamp_value(info) == bc.UNKNOWN)
    check("the unknown stamp is still emitted", 'content="unknown"' in bc.meta_tags(info))


def test_the_meta_block_omits_a_time_it_does_not_have():
    with_t = bc.meta_tags(bc.build_commit(env={}, git=fake_git()))
    check("a known commit time is emitted", 'name="build-commit-time"' in with_t)
    without = bc.meta_tags({"sha": HEAD7, "dirty": False, "commit_time": None})
    check("an unknown commit time is omitted, not written as 0",
          'name="build-commit-time"' not in without)
    check("the sha survives without a time", 'content="%s"' % HEAD7 in without)


def test_what_the_builders_emit_is_what_the_reader_parses():
    # The two halves are written and read in different files; this is the one
    # case that pins them to the same string, so a change to either that does
    # not change the other fails here instead of in production.
    body = head(bc.meta_tags(bc.build_commit(env={}, git=fake_git())))
    got = qa.parse_commit_stamp(body)
    check("round trip: builder output parses as present", got["state"] == "present")
    check("round trip: sha survives", got["sha"] == HEAD7)
    check("round trip: time survives", got["commit_time"] == 1786427284)


# ---------------------------------------------------------------- the reader


def test_a_stamp_matching_head_reads_as_current():
    got = qa.parse_commit_stamp(head(STAMP % HEAD7, STAMP_T % "1786427284"))
    level, line = qa.commit_verdict(got, HEAD7, behind=0)
    check("matching stamp → ok", level == "ok")
    check("matching stamp says CURRENT", "CURRENT" in line)
    check("matching stamp does not say UNKNOWN", "UNKNOWN" not in line)


def test_a_stamp_behind_head_says_how_far_behind():
    got = qa.parse_commit_stamp(head(STAMP % OLD7))
    level, line = qa.commit_verdict(got, HEAD7, behind=5)
    check("behind → warn, not ok", level == "warn")
    check("behind says STALE", "STALE" in line)
    check("behind names the count", "5 commits behind" in line)
    check("behind names the deployed commit", OLD7 in line)
    _, one = qa.commit_verdict(got, HEAD7, behind=1)
    check("one commit behind is singular", "1 commit behind" in one)


def test_a_deploy_with_no_stamp_at_all_reads_as_unknown_not_current():
    # THE CASE THIS WHOLE TASK IS ABOUT. banyan.city on 2026-08-10 was serving a
    # 36-hour-old build, and every check we had was green. An old deploy carries
    # no stamp, and a reader that treats "no stamp" as "nothing to complain
    # about" has rebuilt the same false green in a new place.
    got = qa.parse_commit_stamp(head('<meta name="description" content="x">'))
    check("no build-commit meta → absent", got["state"] == "absent")
    level, line = qa.commit_verdict(got, HEAD7, behind=None)
    check("absent → warn, never ok", level == "warn")
    check("absent says UNKNOWN in as many words", "UNKNOWN" in line)
    check("absent explicitly denies being evidence of currency",
          "not evidence that it is current" in line)
    check("absent does not claim CURRENT", "CURRENT" not in line)


def test_a_build_that_stamped_unknown_is_kept_apart_from_one_that_stamped_nothing():
    got = qa.parse_commit_stamp(head(STAMP % "unknown"))
    check("`unknown` is its own state, not `absent`", got["state"] == "unknown")
    level, line = qa.commit_verdict(got, HEAD7)
    check("`unknown` → warn", level == "warn")
    check("`unknown` says UNKNOWN", "UNKNOWN" in line)
    check("`unknown` names its own cause, not an old deploy",
          "could not read its own commit" in line)


def test_a_dirty_deploy_is_not_current_even_when_its_sha_matches_head():
    # A dirty build sits on HEAD's sha while containing bytes HEAD does not
    # have. Matching on the sha alone would call it current; it is not, and
    # nothing can make it checkable, so it warns.
    got = qa.parse_commit_stamp(head(STAMP % (HEAD7 + "-dirty")))
    check("-dirty parses as present", got["state"] == "present")
    check("-dirty is flagged", got["dirty"] is True)
    check("-dirty keeps the base sha readable", got["sha"] == HEAD7)
    level, line = qa.commit_verdict(got, HEAD7, behind=0)
    check("-dirty → warn even though the sha matches HEAD", level == "warn")
    check("-dirty says the tree was uncommitted", "UNCOMMITTED" in line)
    check("-dirty does not say CURRENT", "CURRENT" not in line)


def test_a_malformed_stamp_is_reported_as_such_and_never_guessed_at():
    for bad in ("deadbeef-ish", "not-a-sha", "", "1234", "15ee724 15ee724"):
        got = qa.parse_commit_stamp(head(STAMP % bad))
        level, line = qa.commit_verdict(got, HEAD7)
        check("malformed %r → malformed state" % bad, got["state"] == "malformed")
        check("malformed %r → warn" % bad, level == "warn")
        check("malformed %r → says UNKNOWN" % bad, "UNKNOWN" in line)


def test_a_commit_this_checkout_has_never_heard_of_is_not_zero_commits_behind():
    # commits_behind() returns None for a sha git cannot resolve. "None" and "0"
    # must not collapse: one means "we cannot tell", the other means "current".
    got = qa.parse_commit_stamp(head(STAMP % "c0ffee1"))
    level, line = qa.commit_verdict(got, HEAD7, behind=None)
    check("unresolvable sha → warn", level == "warn")
    check("unresolvable sha → UNKNOWN", "UNKNOWN" in line)
    check("unresolvable sha suggests the real causes",
          "does not have" in line and "another branch" in line)


def test_a_deploy_ahead_of_this_checkout_is_not_reported_as_stale():
    got = qa.parse_commit_stamp(head(STAMP % OLD7))
    level, line = qa.commit_verdict(got, HEAD7, behind=0)
    check("ahead → warn", level == "warn")
    check("ahead says AHEAD, not STALE", "AHEAD" in line and "STALE" not in line)


def test_a_page_that_could_not_be_read_is_its_own_answer():
    got = qa.parse_commit_stamp(None)
    check("unreadable body → unreadable state", got["state"] == "unreadable")
    level, line = qa.commit_verdict(got, HEAD7)
    check("unreadable → warn", level == "warn")
    check("unreadable → UNKNOWN", "UNKNOWN" in line)


def test_no_non_answer_can_ever_read_as_ok():
    # The invariant behind every case above, asserted once as an invariant so a
    # future state added to parse_commit_stamp cannot quietly default to green.
    bodies = [
        None,
        head(),
        head(STAMP % "unknown"),
        head(STAMP % "zzzzzzz"),
        head(STAMP % (HEAD7 + "-dirty")),
    ]
    for b in bodies:
        stamp = qa.parse_commit_stamp(b)
        for behind in (None, 0, 3):
            level, _ = qa.commit_verdict(stamp, HEAD7, behind=behind)
            if stamp["state"] == "present" and not stamp["dirty"]:
                continue
            check("a %s stamp is never ok (behind=%s)" % (stamp["state"], behind),
                  level == "warn")


HERE = os.path.dirname(os.path.abspath(__file__))


def source(name):
    with open(os.path.join(HERE, name), encoding="utf-8", errors="replace") as fh:
        return fh.read()


def test_all_three_builders_route_through_the_stamp():
    # ALL THREE, because the gate probes /status and that page is NOT written
    # by build_site.page() — build_sim.py hand-writes its own <head>. A stamp
    # that landed in page() alone would leave the one page the freshness check
    # actually reads blind, and every other page stamped, which looks done.
    site = source("build_site.py")
    check("build_site.page() emits the stamp",
          "build_commit.meta_tags()" in site and "{build_meta}" in site)
    sim = source("build_sim.py")
    check("build_sim.py stamps its own hand-written head",
          "build_commit.meta_tags()" in sim)
    pulse = source("build_pulse.py")
    check("build_pulse.py writes only through page(), so it inherits the stamp",
          "from build_site import page" in pulse
          and pulse.count("write_text(") == 1)


def test_the_built_pages_carry_a_stamp_the_reader_can_read():
    # Against _site/ when there is one. Skipped rather than failed where the
    # site has not been built (CI's lint job does not build), because "not
    # built here" is not the same finding as "built without a stamp" — the
    # distinction this whole file is about, applied to itself.
    site = os.path.join(HERE, "..", "_site")
    for name in ("index.html", "status.html", "pulse.html"):
        p = os.path.join(site, name)
        if not os.path.isfile(p):
            print("  --  _site/%s not built here — skipped, not passed" % name)
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            got = qa.parse_commit_stamp(fh.read())
        check("_site/%s carries a readable build-commit stamp" % name,
              got["state"] in ("present", "unknown"))


def main():
    print("BUILD-COMMIT STAMP — writer")
    test_a_clean_checkout_stamps_the_commit_it_is_sitting_on()
    test_a_build_from_an_uncommitted_tree_refuses_to_claim_a_clean_sha()
    test_a_build_that_cannot_see_git_falls_back_to_what_the_platform_says()
    test_a_container_dropping_beside_a_platform_checkout_is_not_an_uncommitted_build()
    test_a_tracked_edit_is_dirty_even_in_a_platform_checkout()
    test_the_exemption_needs_the_platform_and_git_to_agree_on_the_commit()
    test_an_untracked_file_on_a_developers_machine_still_dirties_the_build()
    test_a_dirty_build_names_the_paths_that_made_it_dirty()
    test_a_build_that_knows_nothing_says_unknown_rather_than_nothing()
    test_the_meta_block_omits_a_time_it_does_not_have()
    test_what_the_builders_emit_is_what_the_reader_parses()
    print("BUILD-COMMIT STAMP — reader (qa_local)")
    test_a_stamp_matching_head_reads_as_current()
    test_a_stamp_behind_head_says_how_far_behind()
    test_a_deploy_with_no_stamp_at_all_reads_as_unknown_not_current()
    test_a_build_that_stamped_unknown_is_kept_apart_from_one_that_stamped_nothing()
    test_a_dirty_deploy_is_not_current_even_when_its_sha_matches_head()
    test_a_malformed_stamp_is_reported_as_such_and_never_guessed_at()
    test_a_commit_this_checkout_has_never_heard_of_is_not_zero_commits_behind()
    test_a_deploy_ahead_of_this_checkout_is_not_reported_as_stale()
    test_a_page_that_could_not_be_read_is_its_own_answer()
    test_no_non_answer_can_ever_read_as_ok()
    print("BUILD-COMMIT STAMP — against the builders and the built site")
    test_all_three_builders_route_through_the_stamp()
    test_the_built_pages_carry_a_stamp_the_reader_can_read()
    print()
    if FAILURES:
        print("✗ %d build-stamp case(s) failed: %s" % (len(FAILURES), ", ".join(FAILURES)))
        return 1
    print("✓ all build-stamp cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
