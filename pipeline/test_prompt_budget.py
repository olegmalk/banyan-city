#!/usr/bin/env python3
"""Pure-logic tests for the prompt token-budget guard.

No torch, no diffusers, no transformers, no GPU: the tokenizer is a fake that
counts whitespace words and the pipeline is a function whose signature carries
the same `max_sequence_length=N` default the real ones do. What is under test is
the part that has to be right when nobody is watching -- that the limit is READ
from the signature rather than written in our source, that an explicit value
wins over the default, that an over-long prompt REFUSES instead of being trimmed
or warned about, and that the refusal names the file and the count.

The regression these stand in for: LTX2's encode_prompt truncates at
max_sequence_length with no warning on any channel (measured on the box
2026-08-14 -- a 2,601-token prompt returned exactly 1024 tokens, silently), and
Wan's default limit is 226 against episode-1 prompts of 207-297 tokens.

Run: python3 pipeline/test_prompt_budget.py
"""

from __future__ import annotations

import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import prompt_budget as pb  # noqa: E402

FAILURES = []
PASSED = 0


def check(cond, label):
    global PASSED
    if cond:
        PASSED += 1
    else:
        FAILURES.append(label)


def eq(got, want, label):
    check(got == want, "%s: got %r want %r" % (label, got, want))


class FakeTokenizer:
    """One token per whitespace-separated word, plus a BOS, like the real ones."""

    def __init__(self, batched=False):
        self.batched = batched

    def __call__(self, text, padding=None, truncation=None,
                 add_special_tokens=True):
        ids = list(range(len(text.split()) + (1 if add_special_tokens else 0)))
        # transformers hands back a mapping; the batched shape is the nested one
        return {"input_ids": [ids] if self.batched else ids}


def ltx_like(prompt=None, negative_prompt=None, do_classifier_free_guidance=True,
             max_sequence_length=1024, device=None):
    """Stands in for LTX2ImageToVideoPipeline.encode_prompt (default 1024)."""


def wan_like(prompt=None, negative_prompt=None, do_classifier_free_guidance=True,
             max_sequence_length=226, device=None):
    """Stands in for WanImageToVideoPipeline.encode_prompt (default 226)."""


def words(n):
    return " ".join(["w"] * n)


# --- the limit is read, not written -----------------------------------------

def test_limit_comes_from_the_signature():
    eq(pb.effective_max_sequence_length(ltx_like), 1024, "ltx default read")
    eq(pb.effective_max_sequence_length(wan_like), 226, "wan default read")


def test_a_changed_default_is_followed_not_ignored():
    """The whole point of reading it: a diffusers bump must move our cliff too."""
    def bumped(prompt=None, max_sequence_length=512):
        pass
    eq(pb.effective_max_sequence_length(bumped), 512, "bumped default followed")
    # and a prompt between the old and new limits must now refuse
    try:
        pb.check_prompt_budget(bumped, FakeTokenizer(), [("p", words(600))])
        check(False, "prompt over the NEW lower limit must refuse")
    except pb.PromptTooLong:
        check(True, "prompt over the NEW lower limit refuses")


def test_explicit_value_wins_over_the_default():
    eq(pb.effective_max_sequence_length(ltx_like, explicit=256), 256,
       "explicit overrides signature default")
    try:
        pb.check_prompt_budget(ltx_like, FakeTokenizer(), [("p", words(300))],
                               explicit=256)
        check(False, "explicit limit must be the one enforced")
    except pb.PromptTooLong:
        check(True, "explicit limit is the one enforced")
    # ... and the same prompt is fine against the signature default
    eq(pb.check_prompt_budget(ltx_like, FakeTokenizer(), [("p", words(300))]),
       1024, "same prompt fits the 1024 default")


def test_missing_or_untyped_limit_refuses_rather_than_guessing():
    def no_param(prompt=None):
        pass

    def none_default(prompt=None, max_sequence_length=None):
        pass

    for fn, label in ((no_param, "no max_sequence_length param"),
                      (none_default, "max_sequence_length=None")):
        try:
            pb.effective_max_sequence_length(fn)
            check(False, "%s must refuse, not guess" % label)
        except pb.PromptTooLong:
            check(True, "%s refuses" % label)


# --- it refuses; it does not trim and it does not merely warn ---------------

def test_over_budget_refuses_and_names_the_file_count_and_loss():
    try:
        pb.check_prompt_budget(
            wan_like, FakeTokenizer(),
            [("prompts/ep1-b04.txt", words(296))], job="beat 04 -> b04.pt")
        check(False, "297 tokens over a 226 limit must refuse")
    except pb.PromptTooLong as e:
        msg = str(e)
        check("prompts/ep1-b04.txt" in msg, "refusal names the file")
        check("297" in msg, "refusal states the token count")
        check("226" in msg, "refusal states the limit")
        check("71" in msg, "refusal states how much text is lost")
        check("LOST" in msg or "DROP" in msg, "refusal says text would be lost")
        check("beat 04 -> b04.pt" in msg, "refusal names the job")


def test_the_negative_is_checked_too():
    """Wan's NEG goes through the same truncating call as the positive."""
    try:
        pb.check_prompt_budget(wan_like, FakeTokenizer(),
                               [("--prompt", words(10)),
                                ("NEG (wan_i2v.py)", words(400))])
        check(False, "an over-long negative must refuse")
    except pb.PromptTooLong as e:
        check("NEG (wan_i2v.py)" in str(e), "refusal names the negative")


def test_every_offender_is_listed_not_just_the_first():
    try:
        pb.check_prompt_budget(wan_like, FakeTokenizer(),
                               [("a.txt", words(300)), ("b.txt", words(400))])
        check(False, "two over-long texts must refuse")
    except pb.PromptTooLong as e:
        check("a.txt" in str(e) and "b.txt" in str(e), "both offenders listed")


# --- and it is inert for everything we actually render today ----------------

def test_todays_worst_case_passes_untouched():
    """684 of 1024 is the worst measured LTX prompt; it must not be disturbed."""
    tok = FakeTokenizer()
    eq(pb.check_prompt_budget(ltx_like, tok, [("worst.txt", words(683))]), 1024,
       "684-token prompt passes")
    eq(pb.check_prompt_budget(ltx_like, tok, [("spec.txt", words(296))]), 1024,
       "297-token job-spec prompt passes")


def test_exactly_at_the_limit_is_allowed():
    """truncation=True at max_length=N keeps N tokens, so N is not a loss."""
    eq(pb.check_prompt_budget(wan_like, FakeTokenizer(), [("p", words(225))]),
       226, "exactly 226 tokens fits")


def test_empty_texts_are_skipped():
    eq(pb.check_prompt_budget(ltx_like, FakeTokenizer(),
                              [("--negative", ""), ("--prompt", None)]), 1024,
       "unused prompt fields are not a defect")


def test_batched_tokenizer_shape_is_counted_correctly():
    """A nested input_ids must not be counted as one token."""
    eq(pb.count_tokens(FakeTokenizer(batched=True), words(9)), 10,
       "batched shape unwrapped")
    eq(pb.count_tokens(FakeTokenizer(batched=False), words(9)), 10,
       "flat shape counted")


# --- the real call sites are wired to it ------------------------------------

def test_call_sites_import_and_use_the_guard():
    """Cheap, but it is what catches a merge that drops the guard line."""
    here = os.path.dirname(os.path.abspath(__file__))
    for name in ("ltx_i2v.py", "wan_i2v.py"):
        with open(os.path.join(here, name), encoding="utf-8") as fh:
            src = fh.read()
        check("from prompt_budget import check_prompt_budget" in src,
              "%s imports the guard" % name)
        check("check_prompt_budget(" in src.split("def stage_encode", 1)[-1],
              "%s calls the guard in stage_encode" % name)
        check("max_sequence_length=1024" not in src
              and "max_sequence_length=226" not in src,
              "%s does not hardcode a limit" % name)


def test_jobs_for_still_serves_a_minimal_namespace():
    """The regression the guard's own wiring caused once: _jobs_for grew a read
    of a.prompt_file, and every hand-built argparse Namespace that had never set
    it (test_pipeline's included) started raising AttributeError. Additive means
    a caller that worked before still works."""
    import argparse
    import json
    import tempfile

    import ltx_i2v

    with tempfile.TemporaryDirectory() as d:
        pf = os.path.join(d, "p.txt")
        with open(pf, "w", encoding="utf-8") as fh:
            fh.write("a short prompt")
        jf = os.path.join(d, "jobs.json")
        with open(jf, "w", encoding="utf-8") as fh:
            json.dump([{"embeds": "e.pt", "prompt_file": pf}], fh)
        # only the keys _jobs_for documents as needed -- no prompt_file/negative_file
        a = argparse.Namespace(jobs=jf, beat=3, seed=1, init="i.png", out="o.mp4",
                               prompt="", negative="")
        jobs = ltx_i2v._jobs_for(a, "encode")
        eq(len(jobs), 1, "minimal namespace yields one job")
        eq(jobs[0].prompt, "a short prompt", "prompt read from the file")
        eq(jobs[0].prompt_file, pf, "source file carried forward for the guard")
        eq(jobs[0].negative_file, "", "absent negative source is empty, not a raise")


def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for fn in tests:
        try:
            fn()
        except Exception:
            FAILURES.append("%s RAISED\n%s" % (fn.__name__, traceback.format_exc()))
    print("prompt_budget: %d checks passed, %d failed" % (PASSED, len(FAILURES)))
    for f in FAILURES:
        print("  FAIL " + f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
