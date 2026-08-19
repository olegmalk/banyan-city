#!/usr/bin/env python3
"""Derive the seed-20260819 probe from a passed goblin-free spec.

Usage: python3 pipeline/derive_seedprobe_0819.py {b01|b18}

WHY THIS SEED AND NOT THE NEXT ONE. `pipeline/loop/darkening-crf-diagnostic-0819.md`
measured six clips and found that `--image-crf` does not cause the progressive
darkening -- two crf-10 takes collapse (b12 -91.05, b20 -25.03) and two crf-10
takes do not (b01 +1.37, b18 +10.14), while every other sampler flag is identical
across all six. The one thing the two collapses share and the four clean takes do
not is **seed 20260819**. This job is the one-variable test of that: the passed
b01 growmotion recipe, unchanged, on 20260819.

Two carriers, because the two collapses were on two different beats and one
clean carrier could always be called beat-specific. b01's crf-33 arm blooms
+73.24, giving a downward seed a bright baseline to show against; b18's two arms
are the flattest pair on record, making it the most sensitive. Beat 1 is a
sapling nub and beat 18 a macro leaf -- no character on screen in either, so both
are clear of the goblin identity freeze.

TWO DEFECTS THIS DERIVATION DOES NOT REPRODUCE, both recorded on the parent:
  * The published clip is given a SEED-TRUE, job-unique name. Every growmotion
    job so far published `01-cold-open-LTX-nubgrow-b-s20260826.mp4` -- a name
    asserting the *plate's* seed on a video, identical across 14 jobs -- because
    the clone substituted the seed everywhere except inside the string it is
    written into. No guard catches it: the `out` path lives in a JSON string
    inside `payload:`, which is never sent to the runner as data.
  * The parent's findings blocks are STRIPPED -- verdict, pick, sweep,
    caveats_not_scored, what_this_licenses. b15/b16/b17 carry inherited pick and
    sweep blocks; the b18 s2/s3/s4 clones stripped NOTHING and carry a full
    `verdict: PASS` on jobs whose clips had not been opened. A reader grepping
    `verdict:` would read a PASS belonging to a different clip.

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

DEFAULT_CHILD_SEED = 20260819

CARRIERS = {
    "b01": {
        "parent_id": "ep2-b01-growmotion-b17-0819",
        "child_id": "ep2-b01-growmotion-s20260819-0819",
        "parent_seed": 20260843,
        "parent_clip": "01-cold-open-LTX-nubgrow-b-s20260826.mp4",
        "child_clip": "01-cold-open-LTX-nubgrow-s20260819.mp4",
        "crf": "33",
        "carrier_note": (
            "b01's crf-33 arm blooms +73.24, so a seed that drags luminance "
            "down has a known-bright baseline to show against."),
    },
    "b21": {
        # DEPTH, not the darkening probe: beat 21's own passing take asks
        # "solved or seed-luck?" in its consumer line and one seed cannot
        # answer it. 20260903 is unused on beat 21 (its series has run 20260902).
        "parent_id": "ep2-b21-daylight-0814",
        "child_id": "ep2-b21-daylight-s20260903-0819",
        "parent_seed": 20260902,
        "child_seed": 20260903,
        "mode": "depth",
        "parent_clip": "21-the-answer-LTX-poolD-0812.mp4",
        "child_clip": "21-the-answer-LTX-daylight-s20260903.mp4",
        "crf": "33",
        "carrier_note": (
            "Beat 21 is the only beat of eight whose definition its verdict "
            "records as fully met, on one seed. Its negative forbids goblin, "
            "creature, person, face and hands, so it is clear of the identity "
            "freeze by construction."),
    },
    "b12": {
        # THE CONVERSE TEST, and the decisive one. b12-stillmotion is a take that
        # DID collapse (-91.05). Every sampler flag is identical to the takes that
        # did not, and seed 20260819 has now been cleared on b01, so the remaining
        # suspects are the plate and the prompt. Re-roll this exact spec on
        # 20260871 -- the flattest seed on record, -0.22 and +10.14 on b18's two
        # arms. If it collapses again on a seed that has never moved luminance
        # anywhere, the seed is exonerated too and the cause is the plate or the
        # prompt. Beat 12 has no goblin on screen.
        "parent_id": "ep2-b12-stillmotion-0819",
        "child_id": "ep2-b12-stillmotion-s20260871-0819",
        "parent_seed": 20260819,
        "child_seed": 20260871,
        "mode": "reseed",
        "parent_clip": "12-related-LTX-stillmotion-crf10-s20260819.mp4",
        "child_clip": "12-related-LTX-stillmotion-crf10-s20260871.mp4",
        "crf": "10",
        "carrier_note": (
            "b12-stillmotion lost 91.05 levels with all three bands falling "
            "together -- the largest collapse on record."),
    },
    "b18": {
        "parent_id": "ep2-b18-tremble-s4-0819",
        "child_id": "ep2-b18-tremble-s20260819-0819",
        "parent_seed": 20260878,
        "parent_clip": "18-the-decision-LTX-ep2-b18-tremble-s4-0819.mp4",
        "child_clip": "18-the-decision-LTX-b18-tremble-s20260819.mp4",
        "crf": "33",
        "carrier_note": (
            "b18's two arms are the flattest pair on record (-0.22 and +10.14), "
            "so it is the most sensitive carrier: any collapse here cannot be "
            "the beat, which has never produced one."),
    },
}

# `caveats_not_scored` and `what_this_licenses` are not caught by the
# verdict|pick|sweep|plate_ack rule the derive scripts share, but they are
# equally a parent's findings and equally wrong on a job with no pixels.
REFUSE = re.compile(
    r"verdict|pick|sweep|plate_ack|caveats_not_scored|what_this_licenses", re.I)

JOBS = Path("pipeline/jobs")


def sub(text: str, old: str, new: str, where: str) -> str:
    """Replace, and refuse if the pattern matched nothing."""
    if old not in text:
        sys.exit("!! %s: %r not found, so the clone is not what it claims." % (where, old))
    n = text.count(old)
    print("   %-46s x%d" % (where, n))
    return text.replace(old, new)


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    if which not in CARRIERS:
        sys.exit("usage: derive_seedprobe_0819.py {%s}"
                 % "|".join(sorted(CARRIERS)))
    c = CARRIERS[which]
    CHILD_SEED = c.get("child_seed", DEFAULT_CHILD_SEED)
    mode = c.get("mode", "probe")
    PARENT_ID, CHILD_ID = c["parent_id"], c["child_id"]
    PARENT_SEED = c["parent_seed"]
    PARENT_CLIP, CHILD_CLIP = c["parent_clip"], c["child_clip"]

    src = JOBS / ("%s.yaml" % PARENT_ID)
    dst = JOBS / ("%s.yaml" % CHILD_ID)
    if not src.exists():
        sys.exit("!! parent %s not found" % src)
    if dst.exists():
        sys.exit("!! %s already exists -- refusing to overwrite a filed spec." % dst)

    raw = src.read_text(encoding="utf-8")

    print("substitutions:")
    # Clip name FIRST. On b18 the parent's clip name embeds the parent job id,
    # so substituting the id first would rewrite the clip name out from under
    # this rule and it would match nothing -- which is exactly the silent
    # no-match this script exists to refuse. It refused; this is the fix.
    raw = sub(raw, PARENT_CLIP, CHILD_CLIP, "published clip name (seed-true)")
    raw = sub(raw, PARENT_ID, CHILD_ID, "job id / every path")
    raw = sub(raw, '\\"seed\\": %d' % PARENT_SEED, '\\"seed\\": %d' % CHILD_SEED,
              "seed inside the jobs-render.json payload")

    spec = yaml.safe_load(io.StringIO(raw))

    refused = sorted(k for k in spec if REFUSE.search(k))
    for k in refused:
        del spec[k]
    print("stripped inherited keys: %s" % (", ".join(refused) or "(none)"))

    if mode == "reseed":
        spec["why"] = (
            "SEED %d on %s, the take that COLLAPSED (-91.05 levels, all three "
            "bands together). ONE VARIABLE off it: seed %d -> %d. 20260871 is the "
            "flattest seed on record (-0.22 and +10.14 on beat 18's two arms). "
            "%s See pipeline/loop/darkening-crf-diagnostic-0819.md."
            % (CHILD_SEED, PARENT_ID, PARENT_SEED, CHILD_SEED, c["carrier_note"]))
        spec["consumer"] = (
            "The darkening diagnostic, and this is the rung that closes it. crf is "
            "already exonerated (four clips, opposite outcomes, identical argv) and "
            "seed 20260819 is already cleared on b01. If this collapses on a seed "
            "that has never moved luminance anywhere, the seed is exonerated too "
            "and the cause is the plate or the prompt -- which is a route decision "
            "someone can then actually make. If it holds, the seed matters on this "
            "plate and not on b01, which is a beat-plate interaction and a "
            "different finding. Not a cut candidate: beat 12 keeps its shipped "
            "take either way.")
        spec["bar"] = {
            "instrument": ("pipeline/luma_drift.py, equal thirds, whole-frame "
                           "BT.601 luma, frames 0/24/48/72/96/120."),
            "the_number_that_decides": (
                "Whole-frame drift f000->f120, TWO-SIDED, |drift| >= 20 levels is "
                "a collapse in either direction. The parent measured -91.05."),
            "FAIL-COLLAPSE-AGAIN": (
                "|drift| >= 20 with bands agreeing in sign. Named as MORE likely, "
                "because crf and seed are both now measured out on other beats "
                "and the plate/prompt is what is left. This is the outcome that "
                "sends the question to the plate.",),
            "PASS-HOLD": (
                "|drift| < 20, or bands disagreeing in sign. Then seed 20260819 "
                "DOES matter on this plate while not mattering on b01, and the "
                "finding is an interaction rather than a single cause. Named as "
                "LESS likely."),
            "band_clause": (
                "A single band moving alone is an OBJECT until eyes say "
                "otherwise -- this beat's 73-frame sibling had a -46.93 mid-band "
                "that was a leaf crossing the frame, not a fade. Bands "
                "disagreeing in sign is never scored as a collapse."),
            "not_scored_here": (
                "The stillness clauses, the bird, the leaf and the grass band are "
                "the parent's bar and are NOT re-litigated. This job asks one "
                "question about luminance. A FAIL on any other axis is recorded "
                "but does not change this verdict."),
            "what_this_licenses": (
                "One clip on one seed. No pick, no promotion, no cut swap, and no "
                "plate or prompt rung filed off it without its own sample."),
        }
    elif mode == "depth":
        spec["why"] = (
            "SEED %d on the passed %s recipe, ONE VARIABLE off %s (seed %d). "
            "Pick depth, not the darkening probe: that parent's own consumer line "
            "asks whether beat 21 is \"solved or seed-luck\" and a single seed "
            "cannot answer it. %s"
            % (CHILD_SEED, which, PARENT_ID, PARENT_SEED, c["carrier_note"]))
        spec["consumer"] = (
            "The beat-21 slot, and the solved-or-seed-luck question its passing "
            "take left open. A second seed holding the four clauses makes the "
            "recipe the reason; a second seed dropping them makes the first take "
            "luck and the beat unsolved. NOT a pick between the two -- which take "
            "ships is R4.")
        spec["bar"] = {
            "carried_unchanged_from_the_parent": (
                "The four clauses in this spec's own `success` key, which the "
                "parent met 4 of 4. They are not restated or reinterpreted here: "
                "a depth seed that changes the bar measures nothing."),
            "the_question_this_answers": (
                "Recipe or luck. One seed meeting a bar cannot distinguish them; "
                "two can start to."),
            "brightness_clause_added": (
                "Whole-frame drift f000->f120 by pipeline/luma_drift.py, "
                "TWO-SIDED, |drift| >= 20 levels in either direction is a "
                "finding. Added on every 121-frame rung from here because two "
                "beats collapsed unnoticed for want of it, and because THIS "
                "beat's negative already forbids 'dark, dusk, dim lighting, low "
                "key' -- so a fade here would also be a negative breach."),
            "band_clause": (
                "A single band moving alone is an OBJECT until eyes say "
                "otherwise. Bands disagreeing in sign is never scored as a fade."),
            "what_this_licenses": (
                "One clip on one seed. No pick, no promotion, no cut swap, no "
                "third seed filed off this one."),
        }
    else:
        spec["why"] = (
            "SEED %d on the passed goblin-free %s recipe, ONE "
            "VARIABLE off %s (seed %d). Not a depth seed: %d is the seed "
            "BOTH measured darkening takes ran on (b12-stillmotion -91.05, "
            "b20-motion -25.03) and that neither clean take used. Every sampler flag "
            "across those six clips is identical, so the seed is the live candidate. "
            "%s See pipeline/loop/darkening-crf-diagnostic-0819.md."
            % (CHILD_SEED, which, PARENT_ID, PARENT_SEED, CHILD_SEED,
               c["carrier_note"]))
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
    for flag, val in (("--frames", "121"), ("--image-crf", c["crf"]),
                      ("--size", "704x1280"), ("--guidance", "2.0")):
        assert "%s %s" % (flag, val) in argv, "%s changed -- not one variable" % flag
    assert "--two-stage" in argv and "--distilled-sigmas" in argv

    assert any(CHILD_CLIP in a for a in back["artifacts"]), back["artifacts"]

    print("\nwrote %s" % dst)
    print("  seed      %d -> %d" % (PARENT_SEED, CHILD_SEED))
    print("  clip      %s" % CHILD_CLIP)
    print("  sampler   unchanged (121f, 704x1280, g2.0, two-stage, "
          "distilled-sigmas, image-crf %s)" % c["crf"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
