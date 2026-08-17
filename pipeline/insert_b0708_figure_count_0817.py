#!/usr/bin/env python3
"""Rule beats 07 and 08's figure count FROM THE SCRIPT, additively.

    python3 pipeline/insert_b0708_figure_count_0817.py --check
    python3 pipeline/insert_b0708_figure_count_0817.py --apply

WHY A SCRIPT AND NOT AN EDITOR. `review/ep2-picks/done-definitions.yaml` is
127 KB of hand-written provenance and it is the file every ep2 beat is judged
from. Lanes are live in this worktree. So it is edited as TEXT by a checked
insert -- sha256 before and after, a byte delta asserted against the exact
payload, a backup written, and a PARSED-VARIANT DIFF proving which keys moved --
the pattern `insert_sapling_canon_drafts_0816.py` and `fix_b19_bounce_0816.py`
set. Three insertions, zero deletions, and NOT ONE EXISTING LINE IS TOUCHED,
following `13bba2ce`, which added 74 lines to this file and removed none.

THE SUPERSEDED TEXT STAYS. Both `done_when` strings are left byte-identical
where they stand. The disagreement between a definition and its correction IS
the record here; that is this file's own convention (`open_question` /
`open_question_ANSWERED_0816`, `plate_lane_0817` /
`plate_lane_0817_CORRECTION`) and it is followed rather than improved on.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "review" / "ep2-picks" / "done-definitions.yaml"

# ---------------------------------------------------------------------------
# The three payloads. Anchors are the LAST line of each block being appended
# to, matched once and only once.
# ---------------------------------------------------------------------------

ANCHOR_07 = """    written: 2026-08-15, retroactively — this beat had NO definition of done and its clips were rendered
      without one.
    status: NO VERDICT YET
"""

ADD_07 = """    figure_count_ruled_from_the_script_0817: 'THE `done_when` ABOVE IS LEFT STANDING UNEDITED AND IS
      WRONG ON ONE CLAUSE. It requires that "the second guard and the field are present". THE SCRIPT
      DOES NOT ASK FOR THE SECOND GUARD AND NEVER DID. node.md, 0:34-0:37, verbatim: "CONFISCATE.
      Guard 1 points at the scavenger, decisive." / "> GUARD 1: So we confiscate the apple." The
      stage direction names ONE GUARD as the actor and THE SCAVENGER as the target of the point.
      That is TWO FIGURES. The second guard appears nowhere in the beat''s line, its dialogue or its
      stage direction, and the requirement was added on 2026-08-15 when this beat''s definition was
      written retroactively -- as its own `written:` field says.
      A SECOND CLAUSE IN THAT SAME `done_when` IS EVIDENCE THAT IT WAS DRAFTED FROM AN IMAGINED
      THREE-FIGURE MASTER RATHER THAN FROM THE SCRIPT: it also demands "the clipboard stays the same
      object in the same hands". The clipboard is GUARD 2''s prop. With Guard 2 out of frame -- which
      is what the script asks for -- that clause has NO SUBJECT IN THE SHOT AT ALL. It is superseded
      with the figure count, for the same reason.
      RULING: beat 07 needs TWO figures, Guard 1 and the scavenger. The three-figure blocker on this
      beat is REMOVED. See `figure_count_ruled_from_the_script_0817` at the top level of this file
      for the rule, its control and the four corroborating lines, and for the narrow limits of what
      this ruling does and does not certify.'
"""

ANCHOR_08 = """    definition_written: 2026-08-15, written retroactively from node.md and NOT from any existing take,
      so it could not be bent to fit the clips that already exist.
    status: NO VERDICT YET
  '15':
"""

ADD_08 = """    figure_count_ruled_from_the_script_0817: 'THE `done_when` ABOVE IS LEFT STANDING UNEDITED AND IS
      WRONG ON ONE CLAUSE. It requires "both guards and the scavenger in frame". THE SCRIPT ASKS FOR
      TWO FIGURES. node.md, 0:37-0:42, verbatim: "INSIDE HIM. Guard 2 lowers the clipboard and points
      at the scavenger''s belly." / "> GUARD 2: The apple is *inside him*, Dren." The stage direction
      names ONE GUARD as the actor and THE SCAVENGER''S BELLY as the target. Guard 1 is not in it.
      THE CLAUSE REFUTES ITSELF, AND THIS IS THE SHORTEST ROUTE TO THE ANSWER. It states its own
      reason: "since a point needs its target visible". The target of this point is THE BELLY. Two
      figures -- the pointing guard and the goblin whose belly it is -- satisfy that purpose
      completely. The literal text over-specifies against its own stated rationale, which is the
      signature of a requirement added for staging comfort rather than derived from the beat.
      THE NAME "DREN" IS NOT A COUNTER-ARGUMENT. Guard 2 addresses his partner by name; addressing
      someone off-screen is ordinary coverage, and the partner is established as present by beats 05,
      06, 09, 10 and 11. A voice does not need a body in the frame.
      RULING: beat 08 needs TWO figures, Guard 2 and the scavenger. The three-figure blocker on this
      beat is REMOVED. See `figure_count_ruled_from_the_script_0817` at the top level of this file.'
"""

ADD_TOP = """figure_count_ruled_from_the_script_0817: 'BEATS 07 AND 08 NEED TWO FIGURES, NOT THREE. A filing lane
  found this contradiction and escalated it rather than deciding it, which was right: beat 07''s
  `done_when` wanted "the second guard and the field", beat 08''s wanted "both guards and the
  scavenger", and the two-figure plate that passed its own bar holds two figures with "Three or more
  figures fails" written into axis 1 of that bar. So both beats appeared to demand a three-figure
  plate that has never existed. RESOLVED AGAINST THE SCRIPT, WHICH IS THE AUTHORITY, AND NOT AGAINST
  EITHER `done_when`.

  THE RULE THE SCRIPT ACTUALLY FOLLOWS: A BEAT REQUIRES ITS ACTOR AND THE TARGET OF ITS ACTION.
  Nothing more. Beat 07 -- actor Guard 1, target the scavenger: two. Beat 08 -- actor Guard 2, target
  the scavenger''s belly: two.

  THE CONTROL THAT PROVES THE RULE WAS NOT FITTED TO THE ANSWER, and it is the reason this is a
  ruling rather than an opinion. BEAT 10 has an equally SINGULAR stage direction -- "Guard 2 flips
  the clipboard around: the back is blank" -- and its `done_when` demands "TWO guards in frame; the
  near one flips the bark board and holds its blank back TOWARD HIS PARTNER". Under the actor-plus-
  target rule that is CORRECT, because the target of beat 10''s gesture IS the partner: Guard 1 has
  just asked "...We confiscate the goblin?" in beat 09 and the blank back is the answer shown to him.
  Same rule, different count, and it lands exactly on the number beat 10''s definition already
  carries. A rule that reproduces an existing correct definition it was not built from is a rule; one
  that only ever produces the convenient answer is not.

  FOUR CORROBORATING LINES, ALL FROM FILES THAT PREDATE THIS RULING.
  1. THIS FILE ALREADY READ BEAT 07 AS TWO FIGURES. `corrections_to_the_brief.beat_07_is_not_goblin_free`:
     "07 CONFISCATE is ''Guard 1 points at the scavenger'' - the goblin is in frame and is the thing
     being pointed at." A guard and the goblin. No second guard anywhere in it.
  2. THE SCRIPT SAYS SO WHEN IT MEANS BOTH GUARDS, IN THE PLURAL, AND IT IS SINGULAR IN 07 AND 08.
     Beat 05: "Two PATROL GUARDS jog in and halt, scanning the field." Beat 11: "The guards walk away
     arguing, backs to camera." Both plural, and both `done_when`s are correctly plural. Beats 07 and
     08 name one guard each.
  3. BEAT 06 IS THE CLEANEST CONTROL IN THE FILE and it settles the grammar question. Its stage
     direction has the IDENTICAL SHAPE to beat 08''s -- "GUARD 2 turns over a clipboard made of bark
     and reads" against "Guard 2 lowers the clipboard and points at the scavenger''s belly" -- and its
     `done_when` asks for ONE guard, and the beat SHIPS off a ONE-GUARD scene plate
     (`beats.06.round_3_result`). Nobody ever thought beat 06 needed both guards. There is no reading
     of the script on which 06 takes one and 08 takes three.
  4. THE SCENE IS NOT A LOCKED THREE-FIGURE MASTER AND ALREADY PROVES IT. Beat 09, which sits BETWEEN
     these two, is "Guard 1''s face works through it, slowly" and its `done_when` is "close on Guard
     1''s face" -- ONE figure. The stretch alternates coverage. A three-figure requirement on 07 and
     08 would be inconsistent with the shot sitting between them.
  And beat 07 is a THREE-SECOND shot (0:34-0:37), the shortest in this stretch, against the cycle-007
  taste note in node.md: "a cut every 4.5s, one speaker each, and every beat''s camera is on the
  referent of its line."

  WHAT THIS REMOVES. The three-figure blocker on beats 07 and 08 is gone; it was never in the script.
  The count objection against `farm-out/ep2-b0708-twofig-mac-0815/08-inside-him-twofig-mac-r3-s0.png`
  is WITHDRAWN -- that plate holds THE RIGHT PAIR for beat 08 (an adult guard and the adult goblin,
  same depth plane, adjacent, "belly reachable by an extended arm", board face clean), and its own
  bar''s "Three or more figures fails" was never in tension with the script, only with a `done_when`.

  WHAT THIS DOES NOT CERTIFY, AND IT WILL BE OVER-READ IF THIS IS NOT SAID. NEITHER BEAT IS UNBLOCKED
  BY THIS RULING; ONLY THE COUNT IS SETTLED. (a) That plate''s guard is BALD, and
  `guard_plates_are_miscast_0816` establishes that NEITHER APPROVED GUARD IS BALD -- A has dark
  cropped hair and wire-rim glasses, B has light sandy hair. It is miscast at the first attribute a
  viewer reads off a human being, exactly like the seventeen prompts that finding was about. (b) Beat
  07''s guard is GUARD 1, who has no clipboard: a plate cast as the board-holding guard is the wrong
  man for it, so beat 07 wants its own two-figure plate. (c) `beats.07` is separately GATED by the
  character-first ruling (`corrections_to_the_brief`). SO THE REMAINING WORK ON BOTH BEATS IS A CAST
  PROBLEM ON A TWO-FIGURE COMPOSITION THAT ALREADY RENDERS -- not a three-figure composition that has
  never existed. That is a materially smaller and better-understood piece of work, and naming it
  correctly is the whole value of this entry.

  THE THREE QUEUED PROBES ARE UNAFFECTED. `ep2-b08-twofig-both`, `ep2-b08-twofig-armonly` and
  `ep2-b07-twofig-turn` ask whether a gesture binds to the GUARD once both figures are fixed by an
  init -- in text-to-image it did not, a pointing arm attaching to the goblin 3 of 3 and a board 9 of
  12 however worded. They are `is_show_content: false` ENGINE PROBES AND ARE NEVER TO BE CUT IN.
  Their question is orthogonal to this one and this ruling neither answers nor cancels it.

  SCOPE, stated because this is a definition edit and not a taste call. Which figures a beat''s own
  script requires in frame is a reading of the founder''s text, and it is corrected here against that
  text with the text quoted. It is NOT a taste-axis score, NOT a trunk/graft call and NOT a pick
  among takes (R4). If the founder reads beats 07 and 08 as three-figure shots his reading governs
  and this entry is superseded in turn -- but nothing in the script as written asks for it, and the
  two `done_when` clauses were authored retroactively by a steward on 2026-08-15, by their own
  admission, not by him.'
"""


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build(text: str) -> str:
    """Return the new text. Every anchor must match EXACTLY ONCE."""
    for name, anchor in (("07", ANCHOR_07), ("08", ANCHOR_08)):
        n = text.count(anchor)
        if n != 1:
            sys.exit("!! anchor %s matches %d times, expected 1. Refusing." % (name, n))
    # Guard against a re-run and against a peer having added the same key.
    for key in ("figure_count_ruled_from_the_script_0817",):
        if key in text:
            sys.exit("!! `%s` is ALREADY in the file. Refusing to double-insert." % key)
    if not text.endswith("\n"):
        sys.exit("!! target does not end in a newline; refusing to append blind.")

    out = text.replace(ANCHOR_07, ANCHOR_07 + ADD_07, 1)
    # Beat 08's payload goes BEFORE the `'15':` line that closes its block, so
    # the anchor is re-assembled with the addition spliced in front of it.
    a8_head, a8_tail = ANCHOR_08.rsplit("  '15':\n", 1)
    out = out.replace(ANCHOR_08, a8_head + ADD_08 + "  '15':\n" + a8_tail, 1)
    out = out + ADD_TOP
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    import yaml  # noqa: E402

    before_txt = TARGET.read_text()
    before_sha = sha(TARGET)
    before = yaml.safe_load(before_txt)
    after_txt = build(before_txt)

    payload = len(ADD_07) + len(ADD_08) + len(ADD_TOP)
    delta = len(after_txt.encode()) - len(before_txt.encode())
    exp = len(ADD_07.encode()) + len(ADD_08.encode()) + len(ADD_TOP.encode())
    print("sha256 before      %s" % before_sha)
    print("bytes  before      %d" % len(before_txt.encode()))
    print("payload chars      %d" % payload)
    print("byte delta         %d   (expected %d)" % (delta, exp))
    if delta != exp:
        sys.exit("!! byte delta != payload. Something other than an append happened.")

    after = yaml.safe_load(after_txt)

    # PARSED-VARIANT DIFF: prove exactly which keys moved, and that no existing
    # key changed value. This is the check that catches an indentation slip
    # swallowing a neighbouring block, which a byte count cannot see.
    added_top = set(after) - set(before)
    removed_top = set(before) - set(after)
    print("top-level added    %s" % sorted(added_top))
    print("top-level removed  %s" % sorted(removed_top))
    if removed_top:
        sys.exit("!! a top-level key disappeared. Refusing.")
    if added_top != {"figure_count_ruled_from_the_script_0817"}:
        sys.exit("!! unexpected top-level additions: %s" % sorted(added_top))

    changed = []
    for k in before:
        if k == "beats":
            continue
        if before[k] != after[k]:
            changed.append(k)
    if changed:
        sys.exit("!! existing top-level values changed: %s" % changed)

    if set(before["beats"]) != set(after["beats"]):
        sys.exit("!! the set of beats changed. Refusing.")
    for b in before["beats"]:
        add = set(after["beats"][b]) - set(before["beats"][b])
        rem = set(before["beats"][b]) - set(after["beats"][b])
        if rem:
            sys.exit("!! beat %s lost keys: %s" % (b, sorted(rem)))
        if add:
            print("beat %-4s added     %s" % (b, sorted(add)))
        if b not in ("07", 8, "08"):
            if before["beats"][b] != after["beats"][b]:
                sys.exit("!! beat %s changed and should not have." % b)
            continue
        # For the two target beats, every PRE-EXISTING key must be untouched --
        # in particular the two superseded `done_when` strings, which are the
        # whole point of leaving the record standing.
        for k in before["beats"][b]:
            if before["beats"][b][k] != after["beats"][b][k]:
                sys.exit("!! beat %s key %r was modified. Refusing." % (b, k))
        print("beat %-4s existing keys all byte-identical (incl. done_when)" % b)

    if not a.apply:
        print("\n--check only: nothing written. Re-run with --apply.")
        return 0

    backup = TARGET.with_suffix(".yaml.bak-b0708-figcount-0817")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(after_txt)
    print("\nbackup             %s" % backup.name)
    print("sha256 after       %s" % sha(TARGET))
    print("bytes  after       %d" % len(TARGET.read_bytes()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
