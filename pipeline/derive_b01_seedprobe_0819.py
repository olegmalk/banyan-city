#!/usr/bin/env python3
"""Derive the seed-20260819 probe from a passed b01 growmotion spec.

WHY THIS SEED AND NOT THE NEXT ONE. `pipeline/loop/darkening-crf-diagnostic-0819.md`
measured six clips and found that `--image-crf` does not cause the progressive
darkening -- two crf-10 takes collapse (b12 -91.05, b20 -25.03) and two crf-10
takes do not (b01 +1.37, b18 +10.14), while every other sampler flag is identical
across all six. The one thing the two collapses share and the four clean takes do
not is **seed 20260819**. This job is the one-variable test of that: the passed
b01 growmotion recipe, unchanged, on 20260819.

b01 is the carrier because its crf-33 arm blooms +73.24 -- a seed that drags
luminance down has a known-bright baseline to show against -- and because beat 1
is a sapling nub with no character on screen, so it is clear of the goblin
identity freeze.

TWO DEFECTS THIS DERIVATION DOES NOT REPRODUCE, both recorded on the parent:
  * The published clip is given a SEED-TRUE, job-unique name. Every growmotion
    job so far published `01-cold-open-LTX-nubgrow-b-s20260826.mp4` -- a name
    asserting the *plate's* seed on a video, identical across 14 jobs -- because
    the clone substituted the seed everywhere except inside the string it is
    written into. No guard catches it: the `out` path lives in a JSON string
    inside `payload:`, which is never sent to the runner as data.
  * The parent's `pick`, `sweep_summary` and `sweep_summary_correction` blocks
    are STRIPPED. b15/b16/b17 all carry them inherited, so a reader grepping
    `pick:` on this job would find a recommendation made before it existed.

Every substitution is asserted to have matched something; a clone that silently
matches nothing is how a job publishes another job's frames under its own name.
Run from the repo root. Writes the spec and prints what it changed; it does not
enqueue.
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import yaml

PARENT_ID = "ep2-b01-growmotion-b17-0819"
CHILD_ID = "ep2-b01-growmotion-s20260819-0819"
PARENT_SEED = 20260843
CHILD_SEED = 20260819
PARENT_CLIP = "01-cold-open-LTX-nubgrow-b-s20260826.mp4"
CHILD_CLIP = "01-cold-open-LTX-nubgrow-s20260819.mp4"

REFUSE = re.compile(r"verdict|pick|sweep|plate_ack", re.I)

JOBS = Path("pipeline/jobs")


def sub(text: str, old: str, new: str, where: str) -> str:
    """Replace, and refuse if the pattern matched nothing."""
    if old not in text:
        sys.exit("!! %s: %r not found, so the clone is not what it claims." % (where, old))
    n = text.count(old)
    print("   %-46s x%d" % (where, n))
    return text.replace(old, new)


def main() -> int:
    src = JOBS / ("%s.yaml" % PARENT_ID)
    dst = JOBS / ("%s.yaml" % CHILD_ID)
    if not src.exists():
        sys.exit("!! parent %s not found" % src)
    if dst.exists():
        sys.exit("!! %s already exists -- refusing to overwrite a filed spec." % dst)

    raw = src.read_text(encoding="utf-8")

    print("substitutions:")
    raw = sub(raw, PARENT_ID, CHILD_ID, "job id / every path")
    raw = sub(raw, '\\"seed\\": %d' % PARENT_SEED, '\\"seed\\": %d' % CHILD_SEED,
              "seed inside b01-jobs-render.json")
    raw = sub(raw, PARENT_CLIP, CHILD_CLIP, "published clip name (seed-true)")

    spec = yaml.safe_load(io.StringIO(raw))

    refused = sorted(k for k in spec if REFUSE.search(k))
    for k in refused:
        del spec[k]
    print("stripped inherited keys: %s" % (", ".join(refused) or "(none)"))

    spec["why"] = (
        "SEED 20260819 on the passed goblin-free b01 growmotion recipe, ONE "
        "VARIABLE off %s (seed 20260843). Not a depth seed: 20260819 is the seed "
        "BOTH measured darkening takes ran on (b12-stillmotion -91.05, "
        "b20-motion -25.03) and that neither clean take used. Every sampler flag "
        "across those six clips is identical, so the seed is the live candidate. "
        "See pipeline/loop/darkening-crf-diagnostic-0819.md." % PARENT_ID)
    spec["consumer"] = (
        "The darkening diagnostic. A PASS (no collapse) clears seed 20260819 and "
        "sends the question to the plate or the prompt; a FAIL (collapse on a "
        "recipe that has never collapsed) identifies the seed and makes every "
        "121-frame rung's seed a thing to check. Either way it closes a question "
        "two verdicts left open. Not a cut candidate and not a pick.")
    spec["bar"] = {
        "instrument": "pipeline/luma_drift.py, equal thirds, whole-frame BT.601 "
                      "luma, frames 0/24/48/72/96/120.",
        "the_number_that_decides": (
            "Whole-frame drift f000->f120. TWO-SIDED, because this recipe family "
            "blooms as readily as it fades and the last bar missed that: "
            "|drift| >= 20 levels is a collapse in either direction."),
        "FAIL-COLLAPSE": (
            "|drift| >= 20 AND all three bands agree in sign. This is the "
            "outcome that would implicate the seed. Named as LESS likely: n=2 "
            "and the mechanism is unproven."),
        "PASS-HOLD": (
            "|drift| < 20, or bands disagreeing in sign. Seed 20260819 is "
            "cleared on this carrier and the darkening belongs to the plate or "
            "the prompt. Named as MORE likely."),
        "band_clause": (
            "A single band moving alone is an OBJECT until eyes say otherwise -- "
            "beat 12's -46.93 was a leaf crossing the mid-ground, not a fade. "
            "Bands disagreeing in sign is never scored as a collapse."),
        "not_scored_here": (
            "Growth quality, colour path, camera lock and plate fidelity are the "
            "parent recipe's bar and are NOT re-litigated. This job asks one "
            "question about luminance."),
        "what_this_licenses": (
            "One clip on one seed. No pick, no promotion, no cut swap, no second "
            "seed, and no claim about any beat other than through the "
            "luminance number."),
    }

    dst.write_text(yaml.safe_dump(spec, sort_keys=False, width=100,
                                  allow_unicode=True), encoding="utf-8")

    # Read back and assert the clone is what it claims.
    back = yaml.safe_load(dst.read_text(encoding="utf-8"))
    assert back["id"] == CHILD_ID, back["id"]
    assert back["task"] == CHILD_ID, back["task"]
    for k in back:
        assert not REFUSE.search(k), "inherited key survived: %s" % k
    # The parent id and seed are allowed -- required, in fact -- in the prose
    # keys that record the derivation. They must not survive anywhere the
    # runner reads: payload keys and values, step argv, artifacts.
    operative = yaml.safe_dump({k: back[k] for k in
                                ("payload", "steps", "artifacts")})
    assert PARENT_ID not in operative, "parent id survives in an operative field"
    assert PARENT_CLIP not in operative, "parent clip name survives"
    assert str(PARENT_SEED) not in operative, "parent seed survives"

    render_json = [v for k, v in back["payload"].items() if "jobs-render" in k]
    assert len(render_json) == 1, render_json
    import json
    entries = json.loads(render_json[0])
    assert len(entries) == 1, entries
    assert entries[0]["seed"] == CHILD_SEED, entries[0]["seed"]
    assert entries[0]["out"].endswith(CHILD_CLIP), entries[0]["out"]
    assert CHILD_ID in entries[0]["out"], entries[0]["out"]

    argv = " ".join(" ".join(str(x) for x in s.get("argv", []))
                    for s in back["steps"])
    for flag, val in (("--frames", "121"), ("--image-crf", "33"),
                      ("--size", "704x1280"), ("--guidance", "2.0")):
        assert "%s %s" % (flag, val) in argv, "%s changed -- not one variable" % flag
    assert "--two-stage" in argv and "--distilled-sigmas" in argv

    assert any(CHILD_CLIP in a for a in back["artifacts"]), back["artifacts"]

    print("\nwrote %s" % dst)
    print("  seed      %d -> %d" % (PARENT_SEED, CHILD_SEED))
    print("  clip      %s" % CHILD_CLIP)
    print("  sampler   unchanged (121f, 704x1280, g2.0, two-stage, "
          "distilled-sigmas, image-crf 33)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
