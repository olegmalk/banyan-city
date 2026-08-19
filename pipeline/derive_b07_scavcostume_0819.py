#!/usr/bin/env python3
"""Derive `ep2-b07-scavcostume-0819` FROM ITS PARENT SPEC, programmatically.

WHY A SCRIPT AND NOT A COPY-PASTE. Two reasons, both from tonight's ladder.

1. ONE VARIABLE, AS A FACT ABOUT THE FILE. The child differs from
   `ep2-b07-twofig-0817` in exactly one rendering input: the `--draft-key`. Every
   other argv token, the whole env block, `needs`, the refs directory, the model
   path -- all of it is copied from the parent's own bytes rather than retyped, so
   "one variable" is checkable instead of asserted. Only the id, the output paths
   that MUST be distinct, and the authoring prose (`success`, `why`, `owner`,
   `consumer`) are rewritten, and the script prints every substitution it made.

2. IT IMPLEMENTS THE GUARD THE LADDER ASKED FOR TONIGHT. Three crf-10 specs were
   derived from crf-33 parents "including the parent's verdict, verdict_measured
   and pick blocks", so a filed job carried a PASS that belonged to a different
   clip and a sweep_summary tallying seeds it never rendered. The ladder's note:
   "a spec-derivation step should refuse to carry a parent's verdict/pick/sweep
   keys into a child, or should rename them on the way through. Cheaper than the
   third occurrence." This refuses, by name, and says which keys it dropped.
   `ep2-b07-twofig-0817` carries a `verdict_0819` block, so the guard is not
   hypothetical here -- it fires on this exact derivation.

WHAT IS DELIBERATELY *NOT* INHERITED, and why that is not a loosening:
`success:`. The parent's bar scores EIGHT terms of which term 5 is the POINT, and
the point is no longer this rung's question -- it was answered in motion tonight
(`ep2-b07-point-motion-0819`, PASS, and its crf-10 child, PASS). Carrying a bar
whose central term the job is not testing is how a spec ends up scored against a
question nobody asked. The child's bar is written fresh, pre-registered here
before the pixels exist, and it is NARROWER, not looser: it keeps the parent's
figure-count and cast clauses verbatim in substance and adds the costume clause
the parent never had. The parent's `success` is quoted in the child under
`parent_bar_not_inherited` so the swap is visible rather than silent.

`frame_count_correction_0817` IS carried, renamed. It is not a verdict: it is the
correction that this refs directory holds 3 distinct images in 4 slots, so the
grid is 12 frames and not 16. Same refs, same sampler, same grid in the child, so
the denominator is the same -- and a child that silently reported "N of 16" would
be counting duplicates as independent evidence, which is the exact error that
correction exists to stop.

$0. Writes one yaml file. No GPU, no network, nothing enqueued.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
JOBS = REPO / "pipeline" / "jobs"
PARENT_ID = "ep2-b07-twofig-0817"
CHILD_ID = "ep2-b07-scavcostume-0819"

PARENT_DRAFT_KEY = "authored_b07_twofig_0817"
CHILD_DRAFT_KEY = "authored_b07_scavcostume_0819"

# Keys a child must never inherit. Matched as prefixes on the top-level key.
FORBIDDEN_PREFIXES = ("verdict", "pick", "sweep")

SUCCESS = (
    "THE BAR, PRE-REGISTERED BEFORE THESE PIXELS EXIST. Twelve frames (3 "
    "distinct reference cells x 4 seeds -- see frame_count_inherited_0819; the "
    "denominator is 12 and never 16), each opened INDIVIDUALLY at native "
    "832x1216 and scored by eye. Report every term and every fail mode, fired "
    "or not.\n"
    "THIS RUNG IS NOT ABOUT THE POINT AND DOES NOT SCORE IT. The point was "
    "settled in MOTION tonight -- ep2-b07-point-motion-0819 PASS and "
    "ep2-b07-point-crf10-0819 PASS, all four clauses, the guard's own arm aimed "
    "at the goblin. A plate for this beat no longer has to contain a gesture, "
    "and a frame that happens to draw one earns nothing here.\n"
    "PASS requires ALL FOUR:\n"
    "  C1 THE SCAVENGER'S GARMENT IS HIS OWN. He wears a patched tunic that is "
    "NOT the guard's pale wrap tunic -- distinguishable at a glance by patches, "
    "seams or colour. This is the one variable and the whole reason for the "
    "rung.\n"
    "  C2 THE GUARD IS STILL CAST CORRECTLY. Dark cropped hair, legible "
    "wire-rim glasses, tan-family wrap tunic, wide white sash. Carried from the "
    "parent's bar unchanged; the guard's cast run in the prompt is "
    "byte-identical, so any regression here is the added tokens' fault and must "
    "be reported as one.\n"
    "  C3 TWO WHOLE FIGURES, ONE DEPTH PLANE. One adult human guard and one "
    "goblin, both wholly in frame, shoulder to shoulder. Carried from the "
    "parent's bar unchanged.\n"
    "  C4 THE GOBLIN IS STILL A GOBLIN. Green skin and pointed ears, not a "
    "human child, and not green paint on a second guard.\n"
    "FAIL MODES, NAMED IN ADVANCE AND ALL REPORTED WHETHER OR NOT THEY FIRE:\n"
    "  P1 COSTUME MERGE UNMOVED -- he still wears the guard's tunic. The "
    "measured baseline is r1-s3 and this is the failure the rung exists to "
    "move.\n"
    "  P2 THE TUNIC LANDS ON THE WRONG MAN -- the GUARD arrives in a patched "
    "tunic. The same broadcast bleed in the other direction, and it would say "
    "`in`-binding does not scope a garment on this checkpoint.\n"
    "  P3 THE PATCHES CLIMB ONTO SKIN OR SKULL -- stitches, seams or grafts on "
    "his head or face. MEASURED 4 of 4 on this checkpoint with `patchwork "
    "cloak` (authored_b02_idfix_r2). `patched tunic` was chosen because beat 08 "
    "sends it with clean skulls 4/4, so this is the specific risk the choice "
    "was made to avoid and it is reported either way.\n"
    "  P4 THE WHITE SASH STILL BLEEDS -- he keeps the guard's sash over his own "
    "tunic. NOT a pass/fail clause: it is a MEASUREMENT this rung takes, "
    "because no term in the prompt places or denies a sash on him. Report the "
    "count out of 12.\n"
    "  P5 THE EYEWEAR STILL BLEEDS -- round wire-rims on the goblin, measured 5 "
    "of 12 on the parent. Also NOT a pass/fail clause and also not addressed by "
    "this rung; report the count so rung D has a baseline.\n"
    "  P6 A THIRD FIGURE -- fired 10 of 12 on the parent's sibling rung. Fails "
    "the frame it fires on.\n"
    "  P7 FRAMING REGRESSION -- a crop that loses either figure's whole body.\n"
    "A PARTIAL IS A FAIL PER FRAME. The rung's own question is answered by the "
    "C1 count out of 12 whether or not any single frame clears all four."
)

WHY = (
    "Beat 07's motion PASSED tonight, both takes, on the first attempt -- so "
    "this beat's blocker is no longer 'can it be animated'. It is that the "
    "PLATE dresses the scavenger in the guard's uniform, which makes a "
    "confiscation read as two officials standing together. That is the last "
    "thing between beat 07 and a cut, and it is a still-plate question with one "
    "variable in it. The cause is named: the parent prompt gives the goblin a "
    "noun phrase with ONE attribute and no garment at all, so the only clothing "
    "terms in the sentence are the guard's and they land on both men -- the "
    "positive-placement law this repo has now hit five times. Five minutes of "
    "local GPU, $0, one draft key, twelve frames."
)

CONSUMER = (
    "BEAT 07'S CUT SLOT, directly and at one remove. The chain is short and "
    "every link exists: this plate -> re-run the exact recipe of "
    "ep2-b07-point-crf10-0819 off the new plate (that spec is a byte-level "
    "template, and its verdict makes crf 10 the per-beat choice for THIS beat "
    "with the motion measurement attached) -> a beat-07 clip whose only "
    "recorded faults are gone. Beat 07 is one of the four slates in "
    "review/ep2-demo-0818. A FAIL IS ALSO CONSUMED: P1 unmoved would say a "
    "garment cannot be scoped by `in` on this checkpoint, which retires the "
    "wording channel for costume and names the next instrument (per-figure "
    "conditioning, already characterised on beat 08) instead of spending a "
    "second wording rung on it."
)

OWNER = (
    "beat 07 judging lane, 2026-08-19 -- filed off its own verdict in the same "
    "pass, because the verdict licensed exactly one next job, the card measured "
    "0 ready / 0 running / 0 backlog, and the backlog does not author work"
)


def substitutions() -> list:
    """(from, to) pairs applied to the parent's TEXT. Order matters."""
    return [
        # the one rendering variable
        (PARENT_DRAFT_KEY, CHILD_DRAFT_KEY),
        # output paths that must be distinct from the parent's
        ("out-b07-twofig-0817", "out-b07-scavcostume-0819"),
        ("farm-out/ep2-b07-twofig-0817", "farm-out/ep2-b07-scavcostume-0819"),
        ("ep2-b07-twofig-0817.sha256", "ep2-b07-scavcostume-0819.sha256"),
        # ids
        ("id: ep2-b07-twofig-0817", "id: ep2-b07-scavcostume-0819"),
        ("task: ep2-b07-twofig-0817", "task: ep2-b07-scavcostume-0819"),
        ("--task\n  - ep2-b07-twofig-0817",
         "--task\n  - ep2-b07-scavcostume-0819"),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    import yaml

    src = JOBS / (PARENT_ID + ".yaml")
    dst = JOBS / (CHILD_ID + ".yaml")
    if dst.exists():
        sys.exit("!! %s already exists. Refusing to overwrite." % dst.name)

    parent = yaml.safe_load(src.read_text(encoding="utf-8"))

    # ---- THE GUARD THE LADDER ASKED FOR -------------------------------------
    dropped = sorted(k for k in parent
                     if k.lower().startswith(FORBIDDEN_PREFIXES))
    if not dropped:
        print("guard              no verdict/pick/sweep keys on the parent "
              "(nothing to drop)")
    for k in dropped:
        print("guard DROPPED      %-28s -- a parent's judgement is not a "
              "child's" % k)

    child = {k: v for k, v in parent.items() if k not in dropped}

    # ---- the argv/id substitutions, applied to text and re-parsed -----------
    text = yaml.safe_dump({"steps": parent["steps"],
                           "artifacts": parent["artifacts"]},
                          sort_keys=False, width=100, allow_unicode=True)
    for frm, to in substitutions():
        n = text.count(frm)
        if n:
            text = text.replace(frm, to)
            print("subst              %-46s x%d" % (frm, n))
    moved = yaml.safe_load(text)
    child["steps"] = moved["steps"]
    child["artifacts"] = moved["artifacts"]

    # the one rendering variable must now be present and the parent's absent
    argv_blob = yaml.safe_dump(child["steps"], allow_unicode=True)
    if PARENT_DRAFT_KEY in argv_blob:
        sys.exit("!! the parent draft key survives in the child's steps. "
                 "Refusing.")
    if argv_blob.count(CHILD_DRAFT_KEY) != 2:
        sys.exit("!! the child draft key appears %d times in steps, expected 2 "
                 "(dry + sample). Refusing."
                 % argv_blob.count(CHILD_DRAFT_KEY))
    print("one variable       --draft-key %s -> %s, on both steps"
          % (PARENT_DRAFT_KEY, CHILD_DRAFT_KEY))

    # every OTHER argv token must be byte-identical to the parent's
    def tokens(steps):
        out = []
        for s in steps:
            for t in s.get("argv") or []:
                out.append(str(t))
        return out
    pt, ct = tokens(parent["steps"]), tokens(child["steps"])
    if len(pt) != len(ct):
        sys.exit("!! argv token count changed (%d -> %d). Refusing."
                 % (len(pt), len(ct)))
    changed = [(x, y) for x, y in zip(pt, ct) if x != y]
    for x, y in changed:
        print("argv               %s\n                -> %s"
              % (x[:88], y[:88]))
    print("argv unchanged     %d of %d tokens byte-identical to the parent"
          % (len(pt) - len(changed), len(pt)))

    # ---- THE ARTIFACT DECLARATION, REBUILT AND NOT INHERITED ---------------
    # The parent declares three png filenames the sampler chooses at render
    # time. box_enqueue's output_path_problems() blocks that, correctly: a
    # declared artifact no step ever NAMES cannot prove anything, because the
    # runner's missing-artifact check is then comparing against a guess. (The
    # parent predates that guard and would be blocked by it today too.)
    #
    # So the child declares the ONE file whose name a step really does write:
    # the publish manifest in farm-out. That path is also what makes the render
    # durable -- farm-out is what the courier pushes.
    #
    # THE HOLE THAT LEAVES, AND THE STEP THAT CLOSES IT. The publish program
    # writes its manifest even when its glob matched nothing, and publish is
    # `allow_fail: true` (deliberately, by the parent's own r3 lesson), so a
    # manifest alone could let a job that drew ZERO frames retire rc 0. Rather
    # than edit the parent's steps -- which would cost the byte-identical argv
    # claim above -- a FOURTH step is APPENDED that counts the published pngs and
    # exits nonzero under 12. It is additive, it is not allow_fail, and it is the
    # only step in this spec that is not the parent's own bytes.
    farm_out = ("C:\\banyan-farm\\courier-box\\farm-out\\" + CHILD_ID)
    child["artifacts"] = [farm_out + "\\" + CHILD_ID + ".sha256"]
    child["steps"] = list(child["steps"]) + [{
        "name": "verify",
        "argv": [
            "C:\\banyan-farm\\venv\\Scripts\\python.exe", "-c",
            'import glob, sys\n'
            'd = "C:/banyan-farm/courier-box/farm-out/%s"\n'
            'p = sorted(glob.glob(d + "/07-confiscate-*.png"))\n'
            'print("published pngs:", len(p))\n'
            'for f in p:\n'
            '    print("   ", f.rsplit("/", 1)[-1])\n'
            'if len(p) < 12:\n'
            '    sys.exit("FAILED: %%d published png(s), expected 12 (3 distinct '
            'reference cells x 4 seeds). A short grid is not a sample, and the '
            'manifest alone cannot tell the difference." %% len(p))\n'
            % CHILD_ID,
        ],
    }]
    print("artifacts          rebuilt: 1 manifest path (the parent's 3 "
          "render-time png names are NOT carried)")
    print("step appended      verify -- counts published pngs, exits nonzero "
          "under 12, not allow_fail")

    # ---- authored prose, rewritten and declared ----------------------------
    child["id"] = CHILD_ID
    child["task"] = CHILD_ID
    child["owner"] = OWNER
    child["consumer"] = CONSUMER
    child["success"] = SUCCESS
    child["why"] = WHY
    child["priority"] = 6
    child["parent_bar_not_inherited"] = (
        "The parent's `success` is NOT carried, and that is a narrowing rather "
        "than a loosening -- see derive_b07_scavcostume_0819.py's docstring. Its "
        "eight-term bar turns on term 5, the POINT, which motion answered "
        "tonight and which this rung does not score. Quoted here in full so the "
        "swap is visible and nobody has to diff two files to find it:\n\n"
        + str(parent["success"]))
    child["derived_from"] = {
        "parent": PARENT_ID + ".yaml",
        "by": "pipeline/derive_b07_scavcostume_0819.py",
        "one_variable": "--draft-key %s -> %s" % (PARENT_DRAFT_KEY,
                                                  CHILD_DRAFT_KEY),
        "also_changed": "id/task, the three output paths that must be distinct, "
                        "priority, and the authoring prose (owner, consumer, "
                        "success, why). Nothing else: every remaining argv "
                        "token, the env block, needs, refs, harness and model "
                        "path are the parent's own bytes.",
        "keys_refused": dropped or "none",
    }
    if "frame_count_correction_0817" in child:
        child["frame_count_inherited_0819"] = dict(
            child.pop("frame_count_correction_0817"),
            inherited_note="Carried from the parent and RENAMED on the way "
                           "through, not silently reused. It is a correction to "
                           "a denominator, not a verdict: same refs directory, "
                           "same sampler, same 3-distinct-refs x 4-seeds grid, "
                           "so this child also draws 12 frames and never 16. "
                           "Reporting N of 16 here would count byte-duplicates "
                           "as independent evidence.")
        print("carried renamed    frame_count_correction_0817 -> "
              "frame_count_inherited_0819")

    # sanity: nothing forbidden survived
    left = [k for k in child if k.lower().startswith(FORBIDDEN_PREFIXES)]
    if left:
        sys.exit("!! forbidden keys survived: %s. Refusing." % left)

    out = yaml.safe_dump(child, sort_keys=False, width=100,
                         allow_unicode=True, default_flow_style=False)
    header = (
        "# 2026-08-19, BEAT 07 PLATE RUNG C: THE SCAVENGER GETS A GARMENT OF HIS\n"
        "# OWN. ONE VARIABLE against ep2-b07-twofig-0817 -- the --draft-key, and\n"
        "# nothing else. DERIVED programmatically by\n"
        "# pipeline/derive_b07_scavcostume_0819.py, which prints every\n"
        "# substitution it makes and REFUSES to carry a parent's verdict/pick/\n"
        "# sweep keys (the parent has a verdict_0819 block; it was dropped).\n"
        "#\n"
        "# THIS IS NOT ANOTHER ATTEMPT AT THE POINT. The point was settled\n"
        "# tonight in MOTION: ep2-b07-point-motion-0819 and its crf-10 child both\n"
        "# PASSED beat 07's pre-registered bar, all four clauses, first attempt.\n"
        "# What those verdicts left standing is the plate, and they narrowed its\n"
        "# blocker to one thing -- the scavenger wears the guard's own pale wrap\n"
        "# tunic and white sash, so a confiscation reads as two officials.\n"
        "#\n"
        "# THE WORDING WAS MEASURED BEFORE THIS SPEC EXISTED, offline and $0, on\n"
        "# the real CLIP through the same render_wave_goblin.check() the dry step\n"
        "# below calls: 70/77 positive, 58/77 negative (byte-identical recipe),\n"
        "# count 1boy == declared 1boy, style anchor PRESENT, ZERO faults,\n"
        "# nothing dropped. The parent measured its recorded 65/77 in the same\n"
        "# run, which is the control. See pipeline/insert_b07_scavcostume_0819.py\n"
        "# for why `patched tunic` and not the canon `patchwork cloak`.\n"
        "#\n"
        "# $0. Local card, no provider, no paid engine. Stills only: no voice\n"
        "# synthesis, no episode assembly, nothing published as footage.\n"
    )

    if not a.apply:
        print("\n--check only: nothing written. Re-run with --apply.")
        return 0
    dst.write_text(header + out, encoding="utf-8")
    print("\nwrote              %s (%d bytes)"
          % (dst.relative_to(REPO), len(out.encode()) + len(header.encode())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
