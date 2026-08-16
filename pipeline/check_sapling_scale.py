#!/usr/bin/env python3
"""Catch a sapling that can double in size, BEFORE a GPU-second is spent on it.

    python3 pipeline/check_sapling_scale.py              # sweep this repo
    python3 pipeline/check_sapling_scale.py --quiet      # findings only
    python3 pipeline/check_sapling_scale.py --all        # include fired receipts
    python3 pipeline/check_sapling_scale.py --root DIR   # sweep a fixture tree

$0, no GPU, no network, no model, no image decode, no yaml round-trip of
anything. Exit 0 when there is no finding, 1 when there is.

THE RULING THIS ENFORCES, 2026-08-16:

    "make sure it has 2 leafs and has a set height, height might be a bit hard
    for the ai to make exact, so dont go crazy on it, just dont make it double
    in size suddenly"

The canon is genomes/sapling/THE-SAPLING.md. Leaf count, leaf shape and fruit
colour are enforced by pipeline/check_canon_drift.py against pipeline/canon.yaml.
THIS file enforces the one thing that is neither a forbidden word nor a required
one: whether the prompt SAYS HOW BIG THE PLANT IS AT ALL.

--------------------------------------------------------------------------
WHY COVERAGE AND NOT CONTRADICTION -- the whole design turns on this
--------------------------------------------------------------------------

check_canon_drift.py already catches prompts that state the WRONG size
(`taller than he is`, six beat-15 payloads) and R4 already reports that our
prompts state two different sizes. Neither can catch the actual cause of the
doubling, which is prompts that state NO size.

That is not a guess. Twelve of episode 2's twenty-one beats show the plant and
until 2026-08-16 nothing in the repo described it, so each beat improvised --
and a prompt that says nothing about scale re-rolls the plant's size every seed.
A STATED height cannot double between two beats. An UNSTATED one always can, and
did: beat 01 rendered a 1-3 pixel hairline stem standing 32% of frame height (the
plate the founder revoked with "its tooooo tall"), while beat 12's prompt asked
for a plant "no taller than the grass around it".

So the check is: every prompt that puts the WHOLE PLANT in frame must carry an
explicit scale anchor. Shots framed as macro or close-up are exempt, because in
them the plant's size is not on screen to be wrong -- see the next section.

--------------------------------------------------------------------------
WHAT THIS CANNOT DO, and one of them is a hole nobody should try to fill
--------------------------------------------------------------------------

1. IT CANNOT MEASURE A PIXEL. It reads words. A prompt that says "40cm" and
   renders a tree passes here and is caught only by an eye.

2. APPARENT HEIGHT IN THE FRAME IS NOT PLANT SIZE, AND NO PIXEL MEASURE ACROSS
   BEATS CAN BE HONEST ABOUT IT. This was tested rather than assumed, on
   2026-08-16, by pulling frames and LOOKING at them:

     * cuts/checklist/002b-b01-5b.mp4 frame 0 -- the whole plant in a wide shot,
       a hairline stem crossing roughly half the frame against an open sky.
     * review/ep2-prov-0809/ltx-002b-b12-prov-v2.mp4 frame 0 -- the SAME plant in
       the SAME node, rendered as an extreme macro: seven broad leaves filling
       the frame edge to edge, no stem base, no grass, no horizon, no scale
       reference of any kind.

   Those two frames differ in apparent leaf size by more than an order of
   magnitude and NEITHER IS A CONTINUITY ERROR -- beat 12's own shots.md calls
   for "tight on the sapling's TWO leaves against the sky". A rule of the form
   "apparent height must not jump between beats" would fire on every correctly
   framed macro in the episode. The measure is not merely unreliable across
   beats; it is measuring the wrong quantity, because it conflates SHOT SCALE
   with PLANT SIZE. That is why macro beats are EXEMPT here rather than
   measured, and why no cross-beat pixel metric is shipped.

3. WITHIN a single clip the camera is locked -- every one of these prompts says
   "static locked framing, the frame never moves" -- so a size change inside one
   clip WOULD be meaningful. It is still not attempted, and the reason is the
   repo's own record: segmenting a small green plant against green grass is the
   exact class in which four trackers were retired for cause in two days -- a
   colour rule that matched ZERO hand pixels, one that could not tell a hand
   from a bald head, a freeze index that called clips frozen while the figure
   rose 35-44% of frame height, and a head tracker whose box sat on the sky
   band. Every one of them was confident. The b01 frame above is the FAVOURABLE
   case (dark plant, bright sky) and even there the apex is against sky while
   the base is buried in grass, so the base -- and therefore the height -- has no
   defined edge.

   THE MANUAL CHECK IS THE HONEST ONE, and the tooling for it already exists:
   build a contact sheet of the plant across beats in story order with
   pipeline/compare_sheet.py or pipeline/build_comparison.py and look once. The
   eye settles "did this double" in seconds and does not need a threshold. A
   guard that cries wolf gets disabled -- the runner watchdog was switched off
   for four days after 60 false restarts in five hours -- so a measure that
   cannot be trusted is worse here than no measure plus a habit of looking.

4. IT ONLY READS PROMPTS THAT CAN STILL RUN. A job spec that already fired is a
   receipt, not an instruction, and re-reporting history forever is what got
   that watchdog turned off. Run status comes from
   pipeline/measured/queue-history.json -- a 573-row completed-run ledger keyed
   on `task` and `spec_file` -- not from a directory listing, because farm-out/
   is pruned and its absence proves nothing. `--all` disables the filter.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FAIL, WARN, EXEMPT, OK = "FAIL", "WARN", "EXEMPT", "OK"

# The plant is in the shot at all.
PLANT = re.compile(r"\bsapling\b|\bseedling\b", re.I)

# An explicit scale anchor: wording that pins how big the plant is. Anything on
# this list makes the size of the plant a stated fact rather than a re-roll.
ANCHORS = {
    "explicit-cm": r"\b40\s?cm\b|\bforty centimet",
    "knee-high": r"\bknee[- ]high\b",
    "shorter-than-goblin": r"\bshorter than (?:he|him)\b|hides almost none of him",
    "grass-height": r"no taller than the grass",
}

# Wording that states the size WRONG. The canon is a relation: knee-high on the
# goblin, ~40 cm, always shorter than he is (THE-SAPLING.md 3.2).
CONTRADICTS = r"\btaller than (?:he|him)\b"

# Framing that takes the whole plant off screen. In these the plant's SIZE is
# not depicted, so it cannot be wrong and an anchor would be meaningless -- see
# the module docstring, item 2, which is the measured reason this list exists.
MACRO = re.compile(
    r"extreme close-up|held macro|\bmacro\b|close-up|tight on|"
    r"thinnest branch|filled edge to edge|fills the frame|"
    r"against (?:a soft|the) sky",
    re.I,
)

# NOT an anchor, and each exclusion is deliberate (THE-SAPLING.md 3.3):
#   `standing tall`  -- POSTURE, not height. taste/steward-model.v1.md A7:
#                       "'Reads tall' is about how the subject sits in the FRAME,
#                       not about the character's stated size." Beat 02 writes
#                       "a tiny 40cm mascot-simple sapling standing tall", which
#                       is the proof: the anchor there is `40cm`, not `tall`.
#   `tiny`, `small`  -- relative adjectives with no referent. "a tiny sapling"
#                       described both the hairline weed and the houseplant.


def read_draft_variants(text):
    """wave-drafts.yaml -> [(beat, variant, prompt)]. Line-based, never parsed.

    421 KB of hand-written provenance; a YAML round-trip would destroy it. Only
    `authored*` block scalars under a numeric beat key are prompts -- the
    comments between them are provenance and must not be read as prompt text.
    """
    beat_re = re.compile(r"^  '?(\d+)'?:\s*$")
    var_re = re.compile(r"^    (authored[A-Za-z_0-9]*):\s*>-\s*$")
    beat, variant, buf, out = None, None, [], []

    def flush():
        nonlocal variant, buf
        if variant is not None:
            out.append((beat, variant, " ".join(x.strip() for x in buf).strip()))
        variant, buf = None, []

    for raw in text.split("\n"):
        m = beat_re.match(raw)
        if m:
            flush()
            beat = int(m.group(1))
            continue
        m = var_re.match(raw)
        if m:
            flush()
            variant = m.group(1)
            continue
        if variant is not None:
            if re.match(r"^      \S", raw):
                buf.append(raw)
            else:
                flush()
    flush()
    return out


def fired_tasks(root):
    """Spec names with a completed run, from the queue-history ledger.

    Content, not a directory listing. farm-out/ is pruned, so 'no directory' is
    not evidence a job never ran -- that mistake is already recorded twice in
    this repo's checkers.
    """
    p = Path(root) / "pipeline" / "measured" / "queue-history.json"
    if not p.exists():
        return None  # cannot tell; caller keeps everything rather than guessing
    try:
        d = json.loads(p.read_text(errors="replace"))
    except (ValueError, OSError):
        return None
    out = set()
    for j in d.get("jobs", []) or []:
        if j.get("task"):
            out.add(str(j["task"]))
        if j.get("spec_file"):
            out.add(os.path.splitext(os.path.basename(str(j["spec_file"])))[0])
    return out


def read_job_payloads(root, skip=frozenset()):
    """pipeline/jobs/*.yaml -> [(spec, promptfile, prompt)] for POSITIVE prompts.

    Line-based for the same reason as wave-drafts: these carry long provenance
    headers, and a commented-out prompt is provenance, not an instruction.

    NEGATIVE files are excluded on purpose. A negative saying `no green fig` or
    `no taller than` is the canon WORKING; counting it as an assertion would
    invert the check -- the same trap that makes a bare-term forbid unusable in
    pipeline/canon.yaml.
    """
    out = []
    for f in sorted(glob.glob(os.path.join(root, "pipeline", "jobs", "*.yaml"))):
        spec = os.path.splitext(os.path.basename(f))[0]
        if spec in skip:
            continue
        try:
            text = open(f, errors="replace").read()
        except OSError:
            continue
        for line in text.split("\n"):
            if line.lstrip().startswith("#"):
                continue
            if "negative" in line.lower() or "prompt.txt" not in line:
                continue
            m = re.match(r"^\s*(\S*prompt\.txt):\s*(.*)$", line)
            if not m:
                continue
            out.append((spec, os.path.basename(m.group(1)), m.group(2)))
    return out


def classify(prompt):
    """-> (verdict, detail). Pure function of the text; no state, no I/O."""
    if re.search(CONTRADICTS, prompt, re.I):
        return FAIL, ("states the sapling is TALLER THAN THE GOBLIN, against the canon "
                      "relation (knee-high, ~40 cm, always shorter than he is) and against "
                      "the voiced VO 'I am forty centimeters tall'")
    hits = [name for name, pat in ANCHORS.items() if re.search(pat, prompt, re.I)]
    if hits:
        return OK, "scale anchored by " + ", ".join(sorted(hits))
    if MACRO.search(prompt):
        return EXEMPT, ("macro/close-up framing: the whole plant is not in shot, so its "
                        "size is not depicted and an anchor would be meaningless")
    return WARN, ("the plant is in frame and NOTHING states how big it is -- an unstated "
                  "height re-rolls every seed, which is how one beat got a hairline weed "
                  "at 32% of frame height and another a plant below the grass")


def run(root, include_fired=False):
    root = str(root)
    findings = []

    wd = Path(root) / "pipeline" / "wave-drafts.yaml"
    if wd.exists():
        for beat, variant, prompt in read_draft_variants(wd.read_text(errors="replace")):
            if not PLANT.search(prompt):
                continue
            v, detail = classify(prompt)
            findings.append((v, f"wave-drafts b{beat:02d}:{variant}", detail))

    fired = None if include_fired else fired_tasks(root)
    skip = fired or frozenset()
    for spec, pf, prompt in read_job_payloads(root, skip):
        if not PLANT.search(prompt):
            continue
        v, detail = classify(prompt)
        findings.append((v, f"jobs/{spec}:{pf}", detail))

    return findings, (fired is not None)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--all", action="store_true",
                    help="include job specs that already fired (receipts)")
    ap.add_argument("--quiet", action="store_true", help="findings only, no banner")
    a = ap.parse_args(argv)

    findings, gated = run(a.root, include_fired=a.all)
    order = {FAIL: 0, WARN: 1, EXEMPT: 2, OK: 3}
    findings.sort(key=lambda f: (order[f[0]], f[1]))
    counts = {lv: sum(1 for f in findings if f[0] == lv) for lv in (FAIL, WARN, EXEMPT, OK)}

    for level, where, detail in findings:
        if a.quiet and level not in (FAIL, WARN):
            continue
        if level in (EXEMPT, OK) and not a.quiet:
            continue
        print(f"  {level:<7} {where}\n          {detail}")

    if not a.quiet:
        print()
        if not gated and not a.all:
            print("  note: queue-history.json unreadable -- fired specs were NOT filtered out")
        print(f"SAPLING-SCALE: fail={counts[FAIL]} unanchored={counts[WARN]} "
              f"exempt-macro={counts[EXEMPT]} anchored={counts[OK]}")
    return 1 if counts[FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
