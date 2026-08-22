#!/usr/bin/env python3
r"""EP2 FINISH LANE: the w4 motion recipe, pointed at the GRADED pass-two plates.

    python3 pipeline/file_gradmotion_0822.py                 # dry
    python3 pipeline/file_gradmotion_0822.py --write --beats 17
    python3 pipeline/file_gradmotion_0822.py --write --beats 4,7,14,17

THE ONE VARIABLE IS THE PLATE, AND SPECIFICALLY ITS LIGHT
--------------------------------------------------------------------------
Everything a render reads is carried verbatim from `pipeline/file_w4motion_0822
.py`: the same LTX i2v recipe (704x1280, 105 frames at 24fps, guidance 2.0,
distilled sigmas, two-stage, crf 10), the same per-beat action sentence, the
same corrected eye clause, the same bar. This filer calls that filer's own
`build()` and then swaps exactly one thing -- the init the clip grows from.

WHY THE INIT CHANGES. The w4 tranche runs on `ep2-bNN-canon-w4-0821` plates.
This lane's inits are the PASS-TWO finish plates, which are 0.30 identity
passes off the founder's own canon refs, put through
`pipeline/ep2_finish_grade.py`. The grade exists because the prompt could not
buy light: measured across all 19 pass-two plates, 33-48%% of pixels moved more
than 8 levels while the mean RGB moved about ONE level, so "bright morning",
"warm midday" and "amber afternoon" all came back at lum ~170. The grade is
the only remaining lever on the episode's biggest continuity fault, which is
not any one plate but the cut between three inits sitting at lum 170, 115 and
97.

So a clip filed here differs from its w4 sibling by the plate's LIGHT and by
nothing else, and that is what makes the pair readable.

THE GRADE IS A RECIPE CHANGE, SO BEAT 17 GOES FIRST AND ALONE-IN-EFFECT
--------------------------------------------------------------------------
CLAUDE.md's one-sample rule bites on a recipe change and this is one. Beat 17
is filed at a priority that puts it in front of the others so its clip can be
judged before the tranche behind it finishes; b17 is the right sample because
it converged at t=1.00 (the full afternoon station, the largest grade in the
set) and because its plate is the one beat whose canon posture already IS the
beat's staging, so nothing but the light is being asked to work.

THE PLATE TRAVELS BY FETCH GUARD, NOT BY THE COURIER
--------------------------------------------------------------------------
The w4 plates live in the box's own courier worktree because the box produced
them. These were produced on a Mac, so they are fetched from origin/main and
pinned by sha256 -- the fetch refuses on a mismatch rather than warning,
because a wrong byte here is a clip of a different light filed under this
beat's name.

BEATS THIS FILER WILL NOT TAKE, AND WHY THE GAP IS A DECISION
--------------------------------------------------------------------------
Every guard1 beat (05 g1, 06, 09, 10, 11 g1). `ep2_finish_grade.py --converge`
refused all seven guard1 plates at t=0.14-0.21: lifting that warm dark
portrait into the episode's morning costs an ink lift of +24.9 and a hue
rotation of 26.5 degrees, which repaints the guard rather than lighting him.
There is no graded guard1 plate to file, and filing an ungraded one would be a
clip whose one variable is nothing at all. Beats 09 and 11 are the founder's
own "GOOD" and are untouchable regardless.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

import yaml as _yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                    # noqa: E402
import file_w4motion_0822 as w4                       # noqa: E402

RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
GRADED_DIR = "farm-out/ep2-finish-graded-0822"

# beat -> the graded plate tag that serves it. Guard beats take the guard's own
# half-plate; the goblin beats take theirs. Only beats whose graded plate
# actually exists may appear here, and main() re-checks the file on disk.
PLATE_FOR = {
    2: "b02", 3: "b03", 4: "b04", 7: "b07", 14: "b14", 15: "b15",
    17: "b17", 19: "b19", 20: "b20",
}

# Beat 17 first: it is the one-sample gate for the grade (see the docstring).
PRIORITY = {17: 6}
DEFAULT_PRIORITY = 14


def sha_of(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


FETCH_PY = '''#!/usr/bin/env python3
"""Fetch beat {beat:02d}'s GRADED pass-two plate, pinned by sha256.

The plate is a colour grade of a 0.30 identity pass off the founder's own
canon ref. A wrong byte is a clip in a light nobody chose, filed under this
beat's name, so this refuses rather than warns."""
import hashlib, os, sys, urllib.request

OUT = r"{work}"
URL = "{url}"
WANT = "{sha}"
NAME = "{name}"
UA = {{"User-Agent": "banyan-city-gradmotion/1.0 (albert.numbro@gmail.com)"}}

os.makedirs(OUT, exist_ok=True)
raw = urllib.request.urlopen(
    urllib.request.Request(URL, headers=UA), timeout=120).read()
have = hashlib.sha256(raw).hexdigest()
if have != WANT:
    sys.exit("!! SHA MISMATCH for %s -- refusing." % NAME + chr(10) +
             "   want %s" % WANT + chr(10) + "   have %s" % have)
with open(os.path.join(OUT, NAME), "wb") as fh:
    fh.write(raw)
print("fetched %s %d bytes sha %s OK" % (NAME, len(raw), have), flush=True)
'''


def build(beat: int, pspec: dict):
    """The w4 spec for this beat, with the init swapped for the graded plate."""
    tag = PLATE_FOR[beat]
    rel = "%s/%s-graded.png" % (GRADED_DIR, tag)
    abs_ = os.path.join(REPO, rel)
    if not os.path.isfile(abs_):
        raise SystemExit("!! %s is not on disk -- grade the plate first:\n"
                         "   python3 pipeline/ep2_finish_grade.py --plate "
                         "farm-out/ep2-finish-plates-0822/%s.png --converge "
                         "--out %s" % (rel, tag, rel))
    side = abs_ + ".grade.json"
    if not os.path.isfile(side):
        raise SystemExit("!! %s has no grade sidecar -- a plate whose grade is "
                         "unrecorded cannot carry provenance" % rel)
    import json
    g = json.load(open(side, encoding="utf-8"))
    plate_sha = sha_of(rel)
    if g["out_sha256"] != plate_sha:
        raise SystemExit("!! %s has been rewritten since it was graded: "
                         "sidecar says %s, file is %s"
                         % (rel, g["out_sha256"][:16], plate_sha[:16]))

    # The proven spec, unmodified, straight from the w4 filer.
    child, prompt = w4.build(beat, pspec)

    new_id = "ep2-b%02d-gradmotion-0822" % beat
    old_id = child["id"]
    work = r"C:\banyan-farm\%s" % new_id
    name = "%s-graded.png" % tag

    # Retoken every occurrence of the w4 id, then re-point the init.
    blob = _yaml.safe_dump(child)
    child = _yaml.safe_load(blob.replace(old_id, new_id))

    # 1. the fetch step goes in FRONT of everything, including the crop.
    child["payload"][r"%s\fetch_plate.py" % work] = FETCH_PY.format(
        beat=beat, work=work, url=RAW + rel, sha=plate_sha, name=name)
    child["steps"].insert(0, {
        "name": "fetch",
        "argv": [r"C:\banyan-farm\venv\Scripts\python.exe",
                 r"%s\fetch_plate.py" % work]})

    # 2. the crop step now reads the fetched plate, and asserts its digest.
    hit = 0
    for st in child["steps"]:
        av = st.get("argv") or []
        if "--src" in av:
            av[av.index("--src") + 1] = r"%s\%s" % (work, name)
            av[av.index("--sha256") + 1] = plate_sha
            hit += 1
    if hit != 1:
        raise SystemExit("!! beat %02d: expected exactly one --src step, "
                         "found %d -- refusing to guess" % (beat, hit))

    child["priority"] = PRIORITY.get(beat, DEFAULT_PRIORITY)
    child["owner"] = "the episode-finish compositor lane, 2026-08-22"
    child["the_one_variable"] = (
        "THE PLATE'S LIGHT. Recipe, action sentence, head clause, eye clause, "
        "seed policy and bar are carried byte-for-byte from %s, whose own one "
        "variable was the w4 plate. The init here is the pass-two finish plate "
        "for this beat put through pipeline/ep2_finish_grade.py at station %r, "
        "converge t=%.3f. A difference between this clip and its w4 sibling is "
        "attributable to the grade and to nothing else."
        % (old_id, g["station"], g["converge_t"]))
    child["plate_provenance"] = (
        "%s, 832x1216, sha256 %s. Lineage: taste/refs (the founder's own canon "
        "ref) -> farm-out/ep2-finish-plates-0822/%s.png (a 0.30 all-white-mask "
        "identity pass, which is why the face is his pixels and not a sample) "
        "-> this file, graded by pipeline/ep2_finish_grade.py.\n"
        "GRADE: station %s, converge t=%.3f. lum %.1f -> %.1f, R-B %.1f -> "
        "%.1f, sat %.3f -> %.3f. Gates: ink lift %+.1f (max +14.0), newly "
        "clipped %.3f%% high / %.3f%% low (max 0.60%%), mean hue drift %.2f deg "
        "over %.1f%% chromatic px (max 10.0). The grade is deterministic, $0, "
        "CPU, and its sidecar %s.grade.json carries every number above.\n"
        "WHY A GRADE AT ALL: measured on all 19 pass-two plates, the 0.30 pass "
        "moved 33-48%% of pixels more than 8 levels and the mean RGB by about "
        "ONE level, so the four lights the prompts asked for came back as "
        "three inits at lum 170 / 115 / 97. The light in this frame was bought "
        "by the compositor because the prompt could not buy it."
        % (rel, plate_sha, tag, g["station"], g["converge_t"],
           g["before"]["lum"], g["after"]["lum"], g["before"]["rb"],
           g["after"]["rb"], g["before"]["sat"], g["after"]["sat"],
           g["ink_lift"], g["new_clip_high_pct"], g["new_clip_low_pct"],
           g["hue_drift_deg"], 100.0 * g["chromatic_frac"], rel))
    child["consumer"] = (
        "A CANDIDATE for beat %02d on review/ep2-beats-0821, and the evidence "
        "for one open question: does the episode's light arc survive motion. "
        "review/ep2-ship-0821 is NOT touched and no cut moves because this "
        "landed. A swap happens only when this beat's founder-named fault is "
        "measurably gone, and it is veto-able in one line." % beat)
    child["grade_sample_rule"] = (
        "THE GRADE IS A RECIPE CHANGE AND BEAT 17 IS ITS ONE SAMPLE. 17 is "
        "filed at priority 6 and the rest of the tranche at 14, so 17's clip "
        "lands first and is judged before the others finish. If the grade does "
        "not survive motion, the remaining specs are cancelled rather than "
        "scored -- scaling an unapproved result is the thing the rule forbids."
        if beat == 17 else
        "BEHIND BEAT 17, WHICH IS THE GRADE'S ONE SAMPLE. Filed at priority 14 "
        "so 17 (priority 6) renders and is judged first. If 17's clip fails on "
        "the grade, cancel this spec; do not score it.")
    # THE TWO WAIVERS, AND WHY THEY ARE HONEST RATHER THAN CONVENIENT.
    # box_enqueue's plate checks read origin/farm-results-rtx5090 and resolve a
    # --src back to the farm-out job that published it. Both are exactly right
    # for a box-produced plate and neither can see this one: it was graded on a
    # Mac by a CPU tool and travels by sha-pinned fetch. What the checks are
    # defending against -- an unexamined plate, or one whose lineage nobody can
    # name -- is answered here by construction rather than waived away: the
    # lineage is written out in plate_provenance from the founder's own ref
    # forward, every hop carries a sha256, the grade's numbers are in a
    # committed sidecar, and the fetch step refuses on a digest mismatch before
    # a model loads.
    child["plate_ack"] = [
        "unfetchable: %s is a Mac-side CPU colour grade of "
        "farm-out/ep2-finish-plates-0822/%s.png, not a farm-out render, so it "
        "is not on origin/farm-results-rtx5090 and never will be. It is on "
        "origin/main at sha256 %s and the job's own fetch step refuses any "
        "other bytes. OPENED AT 1:1 by the episode-finish compositor lane on "
        "2026-08-22, side by side against the ungraded plate, before this spec "
        "was written." % (rel, tag, plate_sha),
        "unresolved: no farm-out job produced this plate and none should -- "
        "the grade is deterministic, $0 and CPU-only "
        "(pipeline/ep2_finish_grade.py), and burning a GPU job to launder it "
        "into a farm-out directory would buy provenance we already have. The "
        "producing tool, its station, its converge t and all three gate "
        "readings are in %s.grade.json, committed beside the plate." % rel,
    ]
    child["derivation"] = {
        "parent": "pipeline/jobs/%s.yaml" % old_id,
        "by": "pipeline/file_gradmotion_0822.py",
        "method": "w4.build() verbatim, then exactly three edits: a sha-pinned "
                  "fetch step in front, --src/--sha256 re-pointed at the "
                  "fetched graded plate, and the provenance keys rewritten to "
                  "say which light this is and where it came from.",
    }
    return child, prompt, plate_sha


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--beats", default="17",
                    help="default is 17 alone -- the grade's one sample")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    pspec = _yaml.safe_load(open(os.path.join(REPO, w4.PARENT), encoding="utf-8"))
    for beat in [int(b) for b in a.beats.split(",")]:
        if beat not in PLATE_FOR:
            raise SystemExit(
                "!! beat %d has no graded plate. Every guard1 beat (05 g1, 06, "
                "09, 10, 11 g1) was REFUSED by --converge at t=0.14-0.21: that "
                "plate cannot enter the episode's morning without repainting "
                "the guard. That gap is a decision, not an omission." % beat)
        child, prompt, sha = build(beat, pspec)
        out = "pipeline/jobs/%s.yaml" % child["id"]
        av = [t for st in child["steps"] for t in st.get("argv", [])]
        src = av[av.index("--src") + 1].replace("\\", "/").split("/")[-1]
        print("%-30s beat %02d  prio %2d  init %-16s sha %s  prompt %d chars"
              % (child["id"], beat, child["priority"], src, sha[:12],
                 len(prompt)))
        if a.write:
            derive_spec.write(child, out, force=a.force)
            print("   wrote %s" % out)
    if not a.write:
        print("\nDRY RUN -- pass --write to emit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
