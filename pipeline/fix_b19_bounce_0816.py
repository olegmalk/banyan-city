#!/usr/bin/env python3
"""Retire the beat-19 head-bounce from the four beat-19 drafts that can still fire.

WHY THIS IS A SCRIPT AND NOT AN EDIT. `pipeline/wave-drafts.yaml` is ~350 KB of
hand-written provenance, most of it comments that a YAML round-trip would
silently destroy (ruamel keeps comments, PyYAML does not, and neither preserves
the fold points these measured token budgets were counted against). So the file
is edited as TEXT, with the house guards: sha256 before and after, a backup, a
byte delta ASSERTED equal to the sum of the intended changes, and a
parsed-variant diff proving that exactly the intended keys moved and nothing
else did. Same shape as `insert_sapling_canon_drafts_0816.py`.

WHAT CHANGED IN THE WORLD. The founder ruled on 2026-08-15: "ok then just make
the fig fall on the ground and the goblin will notice it", superseding "lets
make it drop on his head". `genomes/sapling/nodes/002b-first-citizen/node.md:118`
already carries it -- "the stem lets go, the fig falls, and lands in the grass
at his feet. He notices." -- and beat 19's `done_when` in
`review/ep2-picks/done-definitions.yaml` makes NO CONTACT WITH HIS BODY
disqualifying. Eight beat-19 drafts in wave-drafts.yaml still asked for the
bounce.

WHICH FOUR MOVE, AND WHY ONLY FOUR. `render_wave_sample.py` and
`goblin_ipa_beat.py` read the prompt out of wave-drafts.yaml AT RUN TIME, so a
draft key is an instruction exactly as long as some job can still name it.
Fireability was decided off the 799-row `pipeline/measured/queue-history.json`
and the `--variant` / `--draft-key` argv of every spec, never off directory
existence (456 of 509 sidecars are untracked, so a directory proves nothing):

  CORRECTED -- can still fire
    authored_staged      held by  pipeline/jobs/ep2-b19-goblin-wave1.yaml
    authored_b19_adult   authored pipeline/jobs/ep2-b19-adultplate-0813.yaml
    authored             no consumer, never fired -- a future job's base text
    authored_b19_scene   no consumer, never fired -- likewise

  LEFT EXACTLY AS THEY ARE -- receipts
    authored_b19_idfix     only consumer ep2-b19-idfix-0812    FIRED rc=0
    authored_b19_idfix_r2  only consumer ep2-b19-idfix-r2-0812 FIRED rc=0
    authored_b19_refresh   only consumer ep2-b19-refresh-0811  FIRED rc=0
    authored_b19_plate     only consumer ep2-b19-plate-0814    FIRED rc=0

  For a fired run whose sidecar is untracked, the draft key is the only
  committed record of the bytes that were actually sent. Editing one would not
  fix a render; it would falsify a receipt. They are stale as to the bounce and
  they lose to the ruling -- they are not instructions.

  `authored_staged` is BOTH: it fired once (ep2-b19-goblin-staged-0811,
  2026-08-11) and is held for another run. It is corrected, because a key that
  can still fire is an instruction first; the 08-11 receipt is that run's
  sidecar and its spec, and neither is touched.

TOKENS. This Mac has no CLIP tokenizer (`sd_prompt._clip_tokenizer()` returns
None), so `render_wave_goblin.py --dry` refuses here rather than lying, and
these budgets are reasoned, not measured. Every replacement is therefore
token-neutral or shorter: `bounces off his head` (4) -> `lands at his feet` (4).
Only `authored`, which is the shortest block on the beat, gets the full
`lands in the grass at his feet`, and it still comes out two tokens under where
it started. This matters: these blocks were measured at 74-76 of 77, and a
positive that grows drops the whole style sentence, after which `check()` dies
on STYLE ANCHOR MISSING with nothing drawn -- how beat 08 r1 and this beat's own
first idfix draft died. The box's preflight `--dry` step measures for real.

WHAT IS NOT DECIDED HERE. The plate requirement (the fruit must START ON THE
STEM) and where his body is at the top of the beat are recorded as open in
done-definitions.yaml and are not invented here. Neither is the plant's height
relative to the goblin: no replacement adds, removes or implies a scale clause.
"""
from __future__ import annotations

import hashlib
import shutil
import sys

SUFFIX = ".bak-before-b19-bounce-0816"

BEAT_NOTE = """    # =======================================================================
    # BEAT 19 -- THE HEAD-BOUNCE IS DEAD. Recorded 2026-08-16.
    #
    # The founder ruled 2026-08-15: "ok then just make the fig fall on the
    # ground and the goblin will notice it", superseding "lets make it drop on
    # his head". node.md:118 carries it in the author's own words -- "the stem
    # lets go, the fig falls, and lands in the grass at his feet. He notices."
    # -- and beat 19's `done_when` in review/ep2-picks/done-definitions.yaml
    # makes NO CONTACT WITH HIS BODY disqualifying: "a take where the fruit
    # touches him fails this beat now, however well it moves."
    #
    # Eight drafts below asked for the bounce. FOUR ARE CORRECTED and FOUR ARE
    # DELIBERATELY NOT, and the split is fireability, read off
    # pipeline/measured/queue-history.json and the --variant/--draft-key argv of
    # every spec -- never off directory existence, because 456 of 509 sidecars
    # are untracked and a directory proves nothing.
    #
    #   CORRECTED, because a job can still name them and this file is read at
    #   RUN TIME, not at authoring time:
    #     authored_staged     -- held by  pipeline/jobs/ep2-b19-goblin-wave1.yaml
    #     authored_b19_adult  -- authored pipeline/jobs/ep2-b19-adultplate-0813.yaml
    #     authored            -- no consumer, never fired; a future job's base text
    #     authored_b19_scene  -- no consumer, never fired; likewise
    #
    #   LEFT ALONE, because their only consumer has already FIRED (all rc=0,
    #   verified by task name against queue-history.json):
    #     authored_b19_idfix     -> ep2-b19-idfix-0812
    #     authored_b19_idfix_r2  -> ep2-b19-idfix-r2-0812
    #     authored_b19_refresh   -> ep2-b19-refresh-0811
    #     authored_b19_plate     -> ep2-b19-plate-0814
    #   For a run whose sidecar is untracked these keys are the only committed
    #   record of the bytes that were actually sent. Correcting one would not
    #   fix a render; it would falsify a receipt. They are stale as to the
    #   bounce and they lose to the ruling. They are receipts, not instructions.
    #
    # `authored_staged` is both -- it fired on 2026-08-11 and is held for
    # another run. A key that can still fire is an instruction first, so it is
    # corrected; that run's receipt is its sidecar and its spec, untouched.
    #
    # WHERE THIS WAS FOUND BEFORE AND NOT FIXED, said plainly because it is the
    # actual failure: three job specs -- ep2-b19-wave-0814, ep2-b19-waveB-0814
    # and ep2-b19-lw-0814 -- already carry the sentence "done-definitions.yaml's
    # own script key for beat 19 still reads 'bounces off his head', which its
    # ruling_0815 killed the same day." All three have FIRED. A defect written
    # into a receipt is a defect recorded in the one place that can never act on
    # it. Those three specs stay exactly as they are; the source they describe
    # is what got fixed.
    #
    # BOX COPY. render_wave_sample.py resolves the drafts as `harness /
    # "wave-drafts.yaml"`, i.e. C:\\banyan-farm\\wave-goblin-prep\\wave-drafts.yaml
    # -- NOT the repo checkout it is handed as --root. That copy was sha256
    # 83b10b2bb1405a2fa4bddb9816989e59bf4a720251dff618723d150cd8a7289a on
    # 2026-08-16 and is NOT touched by this change. It must be refreshed from
    # this file before either live beat-19 job fires, or the box will render the
    # bounce under the new job id and nobody will see it in the frames.
    # =======================================================================
"""

# (label, old, new). Every `old` was sliced out of the file itself rather than
# retyped, so an em-dash or a fold point cannot drift.
EDITS = [
    (
        "beat-19 note",
        '  19:\n'
        '    slug: the-drop\n'
        '    kind: goblin\n'
        '    tag: 1boy\n'
        '    extra_neg: full\n'
        '    gist: fig drop\n',
        '  19:\n'
        '    slug: the-drop\n'
        '    kind: goblin\n'
        '    tag: 1boy\n'
        '    extra_neg: full\n'
        '    gist: fig drop\n'
        + BEAT_NOTE,
    ),
    (
        "authored_b19_scene",
        '    authored_b19_scene: >-\n'
        '      A small goblin man, {{GOBLIN}}, lean and wiry, narrow angular skull, adult, solo, in\n'
        '      green summer grass, a treeline and pale sky behind, a deep purple-violet fig, green\n'
        '      at its neck, drops from the sapling and bounces off his head. Cinematic lighting,\n',
        '    # -- CORRECTED 2026-08-16, the head-bounce ruling (see the beat note above).\n'
        '    # `bounces off his head` -> `lands at his feet`: four tokens for four, because\n'
        '    # this draft was measured at 76/77 and has no room for the longer form. Nothing\n'
        '    # else moves -- the purple fig, the scene clause and the light are untouched.\n'
        '    authored_b19_scene: >-\n'
        '      A small goblin man, {{GOBLIN}}, lean and wiry, narrow angular skull, adult, solo, in\n'
        '      green summer grass, a treeline and pale sky behind, a deep purple-violet fig, green\n'
        '      at its neck, drops from the sapling and lands at his feet. Cinematic lighting,\n',
    ),
    (
        "authored_b19_adult",
        '    authored_b19_adult: >-\n'
        '      A small goblin man, {{GOBLIN}}, lean and wiry, narrow angular skull, adult, solo,\n'
        '      as a deep purple-violet fig, green at its neck, drops from the sapling beside\n'
        '      him and bounces off his head.\n',
        '    # -- CORRECTED 2026-08-16, the head-bounce ruling (see the beat note above).\n'
        '    # `bounces off his head` -> `lands at his feet`, token-neutral. THIS KEY IS\n'
        '    # LIVE: it is the text ep2-b19-adultplate-0813 (state: authored) will send\n'
        '    # when it fires, which is why it is corrected rather than left as written.\n'
        '    authored_b19_adult: >-\n'
        '      A small goblin man, {{GOBLIN}}, lean and wiry, narrow angular skull, adult, solo,\n'
        '      as a deep purple-violet fig, green at its neck, drops from the sapling beside\n'
        '      him and lands at his feet.\n',
    ),
    (
        "authored",
        '    authored: >-\n'
        '      A small goblin boy, {{GOBLIN}}, solo, stops mid-step as a ripe fig drops\n'
        '      from a tiny sapling standing tall, bounces off his head, and lands in the\n'
        '      grass. Static camera, amber afternoon, cinematic lighting, detailed,\n',
        '    # -- CORRECTED 2026-08-16, the head-bounce ruling (see the beat note above).\n'
        '    # `bounces off his head, and lands in the grass` -> `and lands in the grass at\n'
        '    # his feet`, node.md:118\'s own words. This is the shortest block on the beat,\n'
        '    # so it can afford the full phrasing and still comes out two tokens under\n'
        '    # where it started. It has no consumer today: beat 19 is not one of the beats\n'
        '    # (2, 15, 20) the ungated goblin_ipa_* crossbeat jobs read `authored` for, so\n'
        '    # nothing that reads those beats is affected by this edit.\n'
        '    authored: >-\n'
        '      A small goblin boy, {{GOBLIN}}, solo, stops mid-step as a ripe fig drops\n'
        '      from a tiny sapling standing tall and lands in the grass at his feet.\n'
        '      Static camera, amber afternoon, cinematic lighting, detailed,\n',
    ),
    (
        "authored_staged",
        '    # PAID FOR by `and lands in the grass`, and that removal is measured, not\n'
        '    # preferred: with it kept, the whole style sentence drops and the anchor\n'
        '    # goes with it. It costs nothing real here \u2014 this renders a STILL, and the\n'
        '    # still is the bounce, not the landing. The motion beat keeps the full\n'
        '    # clause in `authored`, which is untouched.\n'
        '    authored_staged: >-\n'
        '      A small goblin boy, {{GOBLIN}}, solo, stops mid-step, surprised face\n'
        '      toward camera, as a ripe fig drops from a tiny sapling rooted in the\n'
        '      ground and bounces off his head. Static camera, medium shot, amber\n',
        '    # PAID FOR by `and lands in the grass`, and that removal is measured, not\n'
        '    # preferred: with it kept, the whole style sentence drops and the anchor\n'
        '    # goes with it. It costs nothing real here \u2014 this renders a STILL, and the\n'
        '    # still is the bounce, not the landing. The motion beat keeps the full\n'
        '    # clause in `authored`, which is untouched.\n'
        '    # -- CORRECTED 2026-08-16. THE PARAGRAPH ABOVE IS SUPERSEDED AND LEFT\n'
        '    # STANDING, because it is the reasoning that has to be visibly withdrawn\n'
        '    # rather than quietly deleted. It was sound and it is now void: "the still\n'
        '    # is the bounce, not the landing" was true only while the bounce existed.\n'
        '    # The founder killed it on 2026-08-15, so on this beat the still IS the\n'
        '    # landing and selling the landing is no longer free.\n'
        '    # `and bounces off his head` -> `and lands at his feet`: token-neutral, four\n'
        '    # for four, so the measured budget behind the rest of that rewrite stands\n'
        '    # and the style anchor is not put at risk. `surprised face toward camera`\n'
        '    # is kept and now carries the noticing the ruling asks for.\n'
        '    # THIS KEY IS LIVE: ep2-b19-goblin-wave1 (state: held) names it, and that\n'
        '    # spec\'s own preflight --dry step will measure this text on the box\'s real\n'
        '    # CLIP tokenizer before anything is drawn.\n'
        '    authored_staged: >-\n'
        '      A small goblin boy, {{GOBLIN}}, solo, stops mid-step, surprised face\n'
        '      toward camera, as a ripe fig drops from a tiny sapling rooted in the\n'
        '      ground and lands at his feet. Static camera, medium shot, amber\n',
    ),
]

# Keys that must come out of the parse BYTE-IDENTICAL. The four receipts, plus
# the four beats whose `authored` the crossbeat jobs read.
RECEIPTS = [
    "authored_b19_idfix",
    "authored_b19_idfix_r2",
    "authored_b19_refresh",
    "authored_b19_plate",
]


def parsed(path_text: str) -> dict:
    """Flatten every beat/key to a plain dict so the diff can be exact."""
    import yaml
    d = yaml.safe_load(path_text)
    beats = d.get("beats", d)
    flat = {}
    for beat, body in beats.items():
        if not isinstance(body, dict):
            continue
        for k, v in body.items():
            flat["%s.%s" % (beat, k)] = v
    return flat


def main(path: str) -> int:
    text = open(path, encoding="utf-8").read()
    before = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print("sha256 before: %s  (%d bytes)" % (before, len(text)))

    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            print("!! %s: anchor appears %d times -- refusing to guess." % (label, n))
            return 4
        if new in text:
            print("!! %s: replacement already present -- refusing to apply twice." % label)
            return 3

    flat_before = parsed(text)

    shutil.copy2(path, path + SUFFIX)

    out, delta = text, 0
    for label, old, new in EDITS:
        out = out.replace(old, new, 1)
        delta += len(new) - len(old)

    if len(out) - len(text) != delta:
        print("!! byte delta %d != intended %d -- a replace() ate something. "
              "NOT writing; the backup is the only clean copy." % (len(out) - len(text), delta))
        return 5

    # PARSED-VARIANT DIFF. Proves exactly which prompt keys changed and that
    # nothing else in 350 KB moved. Comments do not survive the parse, which is
    # the point: this checks the payload, the byte delta checks the prose.
    flat_after = parsed(out)
    changed = sorted(k for k in set(flat_before) | set(flat_after)
                     if flat_before.get(k) != flat_after.get(k))
    expected = sorted(["19.authored", "19.authored_b19_scene",
                       "19.authored_b19_adult", "19.authored_staged"])
    print("parsed keys before/after: %d / %d" % (len(flat_before), len(flat_after)))
    print("changed keys: %s" % (changed or "NONE"))
    if changed != expected:
        print("!! expected exactly %s -- refusing to write." % expected)
        return 6
    for r in RECEIPTS:
        k = "19.%s" % r
        if flat_before.get(k) != flat_after.get(k):
            print("!! receipt %s moved -- refusing to write." % r)
            return 7
        if "bounces off his head" not in (flat_after.get(k) or ""):
            print("!! receipt %s no longer carries its recorded text." % r)
            return 7
    for k in expected:
        v = flat_after[k]
        if "bounce" in v or "his head" in v:
            print("!! %s still asks for the bounce." % k)
            return 8
        if "lands at his feet" not in v and "lands in the grass at his feet" not in v:
            print("!! %s has no landing." % k)
            return 8

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    after = hashlib.sha256(out.encode("utf-8")).hexdigest()
    print("sha256 after:  %s  (%d bytes, %+d)" % (after, len(out), delta))
    print("corrected: %s" % ", ".join(k.split(".", 1)[1] for k in expected))
    print("receipts left byte-identical: %s" % ", ".join(RECEIPTS))
    print("backup:    %s%s" % (path, SUFFIX))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "pipeline/wave-drafts.yaml"))
