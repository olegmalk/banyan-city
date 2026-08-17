#!/usr/bin/env python3
r"""Guards on the drafts-provenance check itself.

WHAT WENT WRONG, 2026-08-17. `box_enqueue.py` promised a run-time drafts check
by name -- "the renderer keeps a second, later check of its own (see
--expect-drafts-sha256) because enqueue time and run time are not the same
moment: `--backlog` work sits for hours" -- and that flag existed in exactly one
place in the repo: that sentence. A false load-bearing docstring is worse than a
stale one, because it closes the investigation: a reader believes the check
exists and stops looking.

So the two things this file exists to prove are not "the code is present":

  1. THE GUARD GOES RED. Every test below that asserts a refusal asserts the
     REFUSAL, not merely that the function returned something. Two of them run
     the sampler as a subprocess and require exit code 12 off its real argv,
     because a check that is present but unwired is the failure mode we found in
     check_canon_drift.py the same day.
  2. IT STAYS INERT WHEN NOT ASKED. The flag was added to shared renderer
     plumbing with jobs in flight. A job that does not pass it must behave
     exactly as it did before the flag existed, and that is asserted too.

Pure functions plus two subprocess runs; no torch, no GPU, no box, no network.
Run: python3 pipeline/test_drafts_guard.py
"""

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_drafts_provenance as cdp                                # noqa: E402
import goblin_ipa_sample as gis                                      # noqa: E402

FAILURES = []

GOOD = "cbb3658ed516e087bbe3725d6c5a83103ed3ab0f9480f0803cf6c713c8e732a5"
STALE = "714d77bc3c3011112222333344445555666677778888999900001111222233ff"


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


# ------------------------------------------------- the run-time guard, in pure form

def test_matching_hash_lets_the_render_proceed():
    check("full 64-digit match: no refusal", gis.drafts_mismatch(GOOD, GOOD) is None)
    check("8-digit prefix match: no refusal",
          gis.drafts_mismatch(GOOD[:8], GOOD) is None)
    check("case and whitespace are not a mismatch",
          gis.drafts_mismatch("  " + GOOD.upper() + "\n", GOOD) is None)


def test_a_changed_wording_is_refused_and_says_so():
    # The failure this whole thing exists for: the job was cleared against one
    # wording and the harness now holds another.
    msg = gis.drafts_mismatch(GOOD, STALE)
    check("changed drafts: refused at all", msg is not None)
    check("changed drafts: says nothing was drawn",
          bool(msg) and "nothing drawn" in msg)
    check("changed drafts: names BOTH hashes so the reader can act",
          bool(msg) and GOOD in msg and STALE in msg)


def test_one_hex_digit_is_enough_to_refuse():
    # A prefix check must not be a fuzzy check. cbb3658e vs cbb3658f is the
    # smallest possible drift and has to fail.
    near = "cbb3658f" + GOOD[8:]
    check("one digit different in the prefix: refused",
          gis.drafts_mismatch("cbb3658e", near) is not None)
    check("one digit different at the tail: refused",
          gis.drafts_mismatch(GOOD, GOOD[:-1] + ("a" if GOOD[-1] != "a" else "b"))
          is not None)


def test_a_prefix_that_is_too_short_refuses_rather_than_passing():
    # 7 digits could collide; the flag must not be quietly weakened by whoever
    # types it. Refusing is the fail-closed direction.
    for weak in ("cbb365", "c", "cbb3658"):
        check("too-short expectation %r refuses (does not pass)" % weak,
              gis.drafts_mismatch(weak, GOOD) is not None)


def test_unusable_expectations_refuse_instead_of_being_ignored():
    for junk in ("not-a-hash", "zzzzzzzz", GOOD + "ff", "cbb3658 e"):
        check("unusable expectation %r refuses" % junk,
              gis.drafts_mismatch(junk, GOOD) is not None)
    check("an unhashable actual refuses",
          gis.drafts_mismatch(GOOD, "unknown") is not None)


def test_absent_flag_is_inert():
    # Live peers, jobs in flight. No flag must mean no behaviour change.
    for absent in (None, "", "   ", "\n"):
        check("absent expectation %r is inert" % absent,
              gis.drafts_mismatch(absent, GOOD) is None)
    check("absent expectation stays inert even with no drafts hash at all",
          gis.drafts_mismatch(None, "") is None)


# ------------------------------------- the run-time guard, off the real command line

def _run_sampler(expect, drafts_bytes=b"04:\n  slug: x\n"):
    """Run the sampler exactly as a job would, and hand back (rc, output).

    A temp harness with only a wave-drafts.yaml in it: the check has to fire
    before render_wave_goblin.py is imported or a weight is touched, so a
    harness that could not possibly render still exercises it.
    """
    with tempfile.TemporaryDirectory() as td:
        harness = Path(td) / "harness"
        harness.mkdir()
        (harness / "wave-drafts.yaml").write_bytes(drafts_bytes)
        argv = [sys.executable, str(HERE / "goblin_ipa_sample.py"),
                "--harness", str(harness), "--root", str(HERE.parent),
                "--refs", td, "--out", td]
        if expect is not None:
            argv += ["--expect-drafts-sha256", expect]
        p = subprocess.run(argv, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180)
        return p.returncode, (p.stdout or "") + (p.stderr or "")


def test_the_sampler_really_exits_12_on_a_mismatch():
    rc, out = _run_sampler("deadbeefcafe1234")
    check("sampler CLI mismatch: rc 12", rc == 12)
    check("sampler CLI mismatch: says DRAFTS CHANGED", "DRAFTS CHANGED" in out)
    check("sampler CLI mismatch: refused before importing the harness module",
          "render_wave_goblin" not in out)


def test_the_sampler_gets_past_a_matching_hash():
    # The green half, and it is not "rc 0" -- this harness cannot render. It is
    # "the check passed and execution moved on", which is what distinguishes a
    # guard from a brick.
    import hashlib
    body = b"04:\n  slug: x\n"
    sha = hashlib.sha256(body).hexdigest()
    rc, out = _run_sampler(sha, drafts_bytes=body)
    check("sampler CLI match: check reports the match",
          "drafts checked at RUN time" in out)
    check("sampler CLI match: rc is NOT the drafts refusal", rc != 12)


def test_a_missing_harness_drafts_file_refuses_when_the_check_was_asked_for():
    with tempfile.TemporaryDirectory() as td:
        harness = Path(td) / "empty"
        harness.mkdir()
        p = subprocess.run(
            [sys.executable, str(HERE / "goblin_ipa_sample.py"),
             "--harness", str(harness), "--root", str(HERE.parent),
             "--refs", td, "--out", td, "--expect-drafts-sha256", GOOD[:8]],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=180)
        check("no drafts file + check asked for: rc 12", p.returncode == 12)
        check("no drafts file: says there is nothing to check against",
              "nothing to check it against" in (p.stdout or "") + (p.stderr or ""))


# ------------------------------------------------------------------ the detector

def test_the_field_is_read_only_from_its_own_line():
    check("reads the field", cdp.sidecar_drafts_sha(
        "shot_beat: 8\ndrafts_sha256: %s\nscored: false\n" % GOOD) == GOOD)
    check("uppercase in a sidecar normalises",
          cdp.sidecar_drafts_sha("drafts_sha256: %s\n" % GOOD.upper()) == GOOD)
    check("no field is None, never a hash", cdp.sidecar_drafts_sha(
        "shot_beat: 8\nscored: false\n") is None)
    # Prose mentions the field name constantly -- the job specs, box_enqueue's
    # docstring, this file. A substring search would read those as evidence.
    check("the field name inside prose is NOT evidence", cdp.sidecar_drafts_sha(
        "note: >-\n  every sidecar carries drafts_sha256 and nothing reads it\n")
        is None)


def test_the_detector_finds_the_divergence():
    files = {"good.yaml": "drafts_sha256: %s\n" % GOOD,
             "stale.yaml": "drafts_sha256: %s\n" % STALE,
             "silent.yaml": "shot_beat: 8\n"}
    res = cdp.audit(sorted(files), GOOD, read=lambda f: files[f])
    check("detector: one matched", [f for f, _ in res["matched"]] == ["good.yaml"])
    check("detector: one diverged", [f for f, _ in res["diverged"]] == ["stale.yaml"])
    check("detector: the fieldless one is neither", res["fieldless"] == ["silent.yaml"])
    check("detector: divergence is rc 1", cdp.verdict(res) == 1)


def test_the_detector_never_calls_an_unidentifiable_tree_a_pass():
    # The rc 0 an empty loop hands back for free is the bug that makes a guard
    # stop guarding without anyone noticing.
    res = cdp.audit(["a.yaml"], GOOD, read=lambda f: "shot_beat: 8\n")
    check("nothing identifiable is rc 2, not 0", cdp.verdict(res) == 2)
    check("an empty audit is rc 2, not 0",
          cdp.verdict(cdp.audit([], GOOD, read=lambda f: "")) == 2)
    res_ok = cdp.audit(["a.yaml"], GOOD, read=lambda f: "drafts_sha256: %s\n" % GOOD)
    check("all matched is rc 0", cdp.verdict(res_ok) == 0)


def test_the_detector_rejects_an_expectation_too_weak_to_mean_anything():
    for weak in ("", "abc1234", "zzzzzzzz", GOOD + "00"):
        want, why = cdp.normalise_expect(weak)
        check("detector rejects expectation %r" % weak, want is None and bool(why))
    want, why = cdp.normalise_expect("  CBB3658E  ")
    check("detector accepts a normalised 8-digit prefix",
          want == "cbb3658e" and why is None)


def test_the_two_implementations_agree():
    # The sampler refuses at render time and the detector reports after the
    # fact. If they disagreed about what "the same wording" means, one of them
    # would be clearing frames the other condemns.
    for expect, actual in ((GOOD, GOOD), (GOOD[:8], GOOD), (GOOD, STALE),
                           ("cbb3658e", "cbb3658f" + GOOD[8:])):
        guard_ok = gis.drafts_mismatch(expect, actual) is None
        det_ok = cdp.matches(expect, actual)
        check("guard and detector agree on (%s..., %s...)"
              % (expect[:8], actual[:8]), guard_ok == det_ok)


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            print("\n" + name)
            fn()
    print("\n%d check(s) failed" % len(FAILURES) if FAILURES
          else "\nALL DRAFTS-GUARD CHECKS PASS")
    for f in FAILURES:
        print("  FAIL  " + f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
