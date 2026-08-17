#!/usr/bin/env python3
"""Append ONE new top-level `verdict_0817` key to each of the six judged specs.

House discipline for hand-written provenance files, borrowed from
insert_b0708_figure_count_0817.py: edit as TEXT, never a YAML round-trip;
sha256 before/after; byte delta asserted EQUAL to the appended text; a
parsed-variant diff proving exactly ONE key added and ZERO keys changed.
"""
import hashlib
import os
import sys

import yaml

JOBS = "/Users/artovonkugler/banyan-city/pipeline/jobs"
# Backups go OUTSIDE the shared worktree: three lanes write here concurrently and
# a .bak next to the spec is a stray file a peer commit would sweep up.
BAK = os.environ.get("VERDICT_BAK_DIR", "/tmp")

VERDICTS = {
    "ep2-b01-canon-0817": """
# ---------------------------------------------------------------------------
# VERDICT, appended 2026-08-17 by the beat-01/18/21 judging lane. The bar above
# was read FIRST, off this committed file, before any frame was opened.
verdict_0817:
  verdict: FAIL-COUNT
  scored_by: beat-18 judging lane, 2026-08-17
  frames_read: 16 of 16, at full resolution off the box copies
  bar_as_written: 'PASS is a seedling with EXACTLY TWO leaves ... bearing ONE small deep purple-violet
    fig ... whole plant in frame. FAIL-COUNT (three or more leaves) is named in this spec as "the
    failure worth reporting, because the two-leaf clause is the half of his ruling this draft exists
    to test".'
  finding: 'FAIL-COUNT on every frame that shows a readable plant. Rows r0 and r1 return leggy stems
    carrying roughly five to eight leaves -- not three, not four, many. Rows r2 and r3 do not fail on
    count so much as collapse: the frame fills with one giant purple mass (a fig-shaped or leaf-shaped
    blob larger than the plant) with a small seedling of three to five leaves in front of it. ZERO of
    16 frames show a two-leaf seedling. The two-leaf clause DOES NOT BIND in this wording.'
  what_did_bind: 'The colour did. Wherever a fruit is legible it is purple or purple-violet, never
    green, red, pale or white -- so FAIL-COLOUR did NOT fire, and the negative''s colour terms
    (`green fig, green fruit, red fruit, white fruit, pale fruit`) are doing their job. That is a real
    result and it is the half of this draft that survives.'
  not_my_call: 'Whether any of these frames is SHIPPABLE (look, framing, the giant-blob composition)
    is R4 and the founder''s. Filed as a founder card, not settled here.'
  filed_off_this: 'NOTHING. A beat whose plant is wrong cannot be rescued by motion -- that is beat
    16''s expensive failure, where a wrong plant IS the shot. Beat 01 gets no seeds.'
  bar_looseness_for_next_rung: 'This bar names attributes per FRAME but never a RATE over the batch,
    so "does the sample pass" was not actually defined. It did not matter here (0 of 16), but the next
    rung should say plainly how many of N must clear before the wording is called bound.'
""",
    "ep2-b01-scale-0817": """
# ---------------------------------------------------------------------------
# VERDICT, appended 2026-08-17 by the beat-01/18/21 judging lane. The bar above
# was read FIRST, off this committed file, before any frame was opened.
verdict_0817:
  verdict: FAIL-COUNT
  also_fired: FAIL-SCALE
  scored_by: beat-18 judging lane, 2026-08-17
  frames_read: 16 of 16, at full resolution off the box copies
  bar_as_written: 'PASS is a seedling with EXACTLY TWO leaves bearing ONE small deep purple-violet fig,
    the whole plant in frame and NO TALLER THAN THE GRASS AROUND IT. FAIL-SCALE = bush or waist height,
    or overtops the grass. FAIL-COUNT = three or more leaves, or one.'
  finding: 'FAIL-COUNT on 16 of 16: every readable plant carries three to eight leaves. FAIL-SCALE
    fires on top of it and in a way the bar did not anticipate -- the grass is mostly NOT IN FRAME at
    all. Where a grass line does appear (r1, r2) it is a thin strip at the bottom that the plant or the
    giant purple mass towers over, so the plant overtops the grass. Rows r2/r3 put a bush-sized purple
    form in frame with grass tiny behind it: that is FAIL-SCALE at its most literal.'
  read_against_its_pair: 'The unanchored arm ep2-b01-canon-0817 failed the SAME axis (FAIL-COUNT, 0 of
    16) on the same reference set. So adding the grass relation changed nothing about leaf count, and
    the grass-relation anchor did not bind here EITHER -- it mostly failed to put grass in the frame.
    Compare beat 21, judged the same day, where the same relation DID bind on 3 of 4 frames. The
    difference is worth the next lane''s attention: beat 21''s draft puts the grass line, treeline and
    sky in the prose; this one leans on `no taller than the grass around it` with a macro-tight frame
    that has no room for grass. The anchor appears to need a FRAME that contains its yardstick.'
  not_my_call: 'Which frame, if any, is shippable -- R4, the founder''s. Filed as a founder card.'
  filed_off_this: 'NOTHING. Beat 01 gets no motion seeds; the plant is wrong and in this beat the plant
    is the entire shot.'
""",
    "ep2-b01-figleafcanon-0817": """
# ---------------------------------------------------------------------------
# VERDICT, appended 2026-08-17 by the beat-01/18/21 judging lane. The bar above
# was read FIRST, off this committed file, before any frame was opened.
verdict_0817:
  verdict: FAIL-COUNT
  scored_by: beat-18 judging lane, 2026-08-17
  frames_read: 16 of 16, at full resolution off the box copies
  bar_as_written: 'PASS: a seedling with EXACTLY TWO leaves, whole plant in frame, one fruit, front-lit.
    The failure this job exists to catch: leaves coming back LOBED and FIVE-FINGERED, *or* three/four/
    many of them. Leaf SHAPE is explicitly NOT scored (steward inference, vetoable). Fruit colour is
    explicitly NOT this lane''s.'
  finding: 'The registered failure is disjunctive and it split cleanly, which makes this the most
    informative of the three beat-01 arms:
    (a) THE LOBE HALF BOUND. The leaves do NOT come back deeply lobed or five-fingered. They come back
        NARROW, POINTED and lance-shaped. Three rounds of mature-tree fig foliage have been suppressed
        by the corrected leaf clause. That is a genuine win and it should be kept.
    (b) THE COUNT HALF DID NOT. Rows r0 and r1 carry four to eight leaves. 0 of 16 show two.
    So the corrected clause fixed the SHAPE it was aimed at and left the COUNT untouched.'
  worse_than_the_bar_expected: 'Rows r2 and r3 do not contain a plant at all. They return a dark red
    MECHANICAL OBJECT -- a hanging lamp or a camera lens with a glowing element -- and in two frames a
    PERSON: r3-w015-s1 is a human hand holding a lens, r3-w015-s3 is an anime face inside a red hood.
    FAIL-PERSON is NOT pre-registered on this bar (its siblings both register it), so it is reported as
    an unregistered defect found rather than used as the verdict axis. Tighten it FORWARD: every plant
    beat''s bar should carry FAIL-PERSON, because the mechanism that produces it is live here -- see
    below.'
  mechanism_note: 'The sidecars say this run conditioned on IP-Adapter Plus at scale 0.6 over steps 0-5,
    with a GOBLIN frame (04-the-footnote-wave1-s2.png) as the reference. On a beat with no character in
    it, that reference is a liability, and the faces and the giant blobs are where it bled through. The
    later reference cells (r2, r3) are consistently the broken ones across ALL THREE beat-01 arms and
    both beat-18 arms judged today. That is a mechanism-level finding, not a wording one.'
  not_my_call: 'The fruit reads RED/pink here rather than purple. This bar hands colour to the founder
    and the fig lane by name, so this lane does NOT fail it on colour -- but the observation is passed
    on, because the founder''s 2026-08-14 ruling is canon-wide and retroactive.'
  filed_off_this: 'NOTHING on beat 01.'
""",
    "ep2-b18-canon-0817": """
# ---------------------------------------------------------------------------
# VERDICT, appended 2026-08-17 by the beat-01/18/21 judging lane. The bar above
# was read FIRST, off this committed file, before any frame was opened.
verdict_0817:
  verdict: PASS-DRAWN
  colour_answer: purple (violet/magenta family)
  scored_by: beat-18 judging lane, 2026-08-17
  frames_read: 16 of 16, at full resolution off the box copies
  bar_as_written: 'SUCCESS IS A READABLE ANSWER, NOT A PURPLE ONE. PASS-DRAWN: ONE fruit in frame,
    hanging from a thin branch, in a held macro. A word in the purple family means the canon as written
    survives this card; red/maroon/crimson/wine/brown/russet means it does not; GREEN would be the most
    informative failure. NO FRUIT IN FRAME is a FAIL. Leaf count, plant height and the final colour
    VERDICT are all excluded by name.'
  finding: 'IT DRAWS. Fruit is in frame in 16 of 16 -- the only registered FAIL for this axis (no fruit)
    never fires. The frames are held macros and the fruit hangs from a thin branch or stem. So the
    canon wording draws on this renderer.'
  colour_measured_not_guessed: 'Hue was measured per frame on the saturated dark fruit mass (circular
    mean of HSV hue). 12 of 16 land in the violet/magenta purple family (269-332 deg); ZERO land in red,
    maroon, wine, brown or russet; ZERO are green. The remaining 2+2 read blue/cyan and are a mask
    artefact -- those are the frames dominated by dark teal LEAVES, not fruit. The chosen plate
    r2-w015-s2 measures 305 deg. So the registered question is answered PURPLE, and THE CANON AS
    WRITTEN SURVIVES THIS CARD. The negative''s colour terms are binding.'
  honest_caveat: 'The purple sits toward magenta rather than deep violet, and the fruit is heavily
    GLOSSY with a hard specular highlight. Neither is a registered fail on THIS bar (gloss is not
    listed here). Both WOULD fail the sibling arm ep2-b18-figleafcanon-0817, which bans gloss and the
    aubergine read by name and did fail. The same pixels clearing one bar and failing the other is not
    a contradiction -- the two bars ask different questions -- but it means beat 18 has a plate that
    certifies the COLOUR WORDING, not a plate certified as matte-and-shippable.'
  not_my_call: 'Whether this plate''s gloss and near-aubergine read are shippable is R4 and belongs to
    the founder. FOUNDER CARD, raised and not settled here.'
  filed_off_this: 'THREE MOTION SEEDS, backlogged 2026-08-17 the moment this verdict was in:
    ep2-b18-tremble-s20260871-0817, -s20260872-, -s20260873-, all off plate r2-w015-s2
    (sha256 ab70a4adec4cb7b69df131febea47af2987d0bbab7e8a4c77810048b29e0a3f1, read off the box manifest
    and recomputed on the pulled copy). The 704x1280 cover crop was PRODUCED and looked at, not
    arithmetic''d. Beat 18 is the only one of the three beats judged today that earned motion.'
  bar_looseness_for_next_rung: 'This bar''s PASS-DRAWN clause says "ONE fruit in frame" but pre-registers
    only "NO FRUIT IN FRAME" as the fail. Most frames actually hold two to four fruits; only about 5 of
    16 hold exactly one. Scored AS WRITTEN that is not a fail here, and it is not being retro-fitted
    into one. Tighten it FORWARD: the next rung should register FAIL-COUNTFRUIT explicitly, the way the
    figleafcanon arm already does, or drop "ONE" from the PASS clause. The plate picked for motion is
    one of the single-fruit frames, so the ambiguity does not travel downstream.'
""",
    "ep2-b18-figleafcanon-0817": """
# ---------------------------------------------------------------------------
# VERDICT, appended 2026-08-17 by the beat-01/18/21 judging lane. The bar above
# was read FIRST, off this committed file, before any frame was opened.
verdict_0817:
  verdict: FAIL-COLOUR
  also_fired: [FAIL-COUNT, FAIL-LEAFSHAPE, FAIL-PERSON]
  scored_by: beat-18 judging lane, 2026-08-17
  frames_read: 16 of 16, at full resolution off the box copies
  bar_as_written: 'PASS is a held macro of a tiny fig sapling''s THINNEST BRANCH against a soft sky,
    carrying EXACTLY TWO wide oval cotyledon leaves with soft round tips, and hanging below them ONE
    small purple fig -- a plain purple teardrop with matte dusty skin. FAIL-COLOUR includes green, red,
    pale or white fruit, an eggplant/aubergine read, or gloss/shine. FAIL-LEAFSHAPE (deeply lobed or
    five-fingered) is named as the failure worth reporting.'
  finding: 'FAIL-COLOUR is the axis that fires hardest and most consistently. Wherever a fruit is
    legible it is PALE GREY (r0-s0, r0-s3, r1-s0, r1-s3, r3-s0, r3-s3), RED (r0-s2), or DARK
    RED-BROWN/RUSSET (r2-s3, r3-s2). Not one frame returns a plain matte purple fig. Pale and red are
    both registered FAIL-COLOUR terms.
    FAIL-COUNT fires everywhere too, in both directions: rows r0 carry five or more leaves, and rows
    r2/r3 carry NONE AT ALL -- bare twigs holding a giant ovoid, which fails "EXACTLY TWO" just as
    surely as eight would.
    FAIL-LEAFSHAPE, the failure this spec said was worth reporting, DOES fire but only narrowly: r0-s3
    returns deeply lobed three-lobed fig leaves and r1-s2 returns palmate ones. So mature-tree foliage
    is still reachable in this wording, on roughly 2 of 16.
    FAIL-COUNTFRUIT fires on r1-s0, r1-s1 and r3-s0 (multiple fruits).
    FAIL-PERSON fires on r3-w015-s2: an anime girl''s face, grey hair, among orange-brown fruits.'
  read_against_its_pair: 'Its sibling ep2-b18-canon-0817 PASSED on the same day, on the same beat, from
    the same card -- fruit drawn, purple measured at 269-332 deg across 12 of 16 frames. So beat 18 is
    NOT colour-blocked as a beat; this particular draft is. The difference between the two drafts is
    where the next rung should look, because one of them gets purple out of this renderer reliably and
    this one gets grey, red and russet.'
  mechanism_note: 'Rows r2 and r3 collapse the same way they do in all three beat-01 arms judged today:
    the IP-Adapter goblin reference bleeds in as a giant ovoid and, in r3-s2, as a face. On beats with
    no character in them that reference is a liability.'
  filed_off_this: 'NOTHING off this arm. Beat 18''s three motion seeds were filed off the arm that
    passed (ep2-b18-canon-0817, plate r2-w015-s2), not off this one.'
""",
    "ep2-b21-scale-0817": """
# ---------------------------------------------------------------------------
# VERDICT, appended 2026-08-17 by the beat-01/18/21 judging lane. The bar above
# was read FIRST, off this committed file, before any frame was opened.
# THIS IS THE FIRST TEST EVER MADE OF THE FOUNDER'S 2026-08-16 SAPLING RULING.
verdict_0817:
  verdict: FAIL-COUNT
  scored_by: beat-18 judging lane, 2026-08-17
  frames_read: 4 of 4, at full resolution off the box copies
  bar_as_written: 'PASS: a sapling with EXACTLY TWO leaves standing NO TALLER THAN THE SURROUNDING
    GRASS, with the grass line, the treeline and the pale sky all in frame, and one thin bare
    side-branch. The failure worth reporting -- "and it is the whole question" -- is the plant coming
    back waist-high, tree-sized, or with three or more leaves. Leaf TILT, fruit colour and leaf SHAPE
    are all excluded by name.'
  ruling_under_test: 'The founder, 2026-08-16, verbatim: "make sure it has 2 leafs and has a set height,
    height might be a bit hard for the ai to make exact, so dont go crazy on it, just dont go double in
    size suddenly." Two independent halves. THE_SAPLING.md records height as a RELATION, not an
    absolute, so the objective tests are (1) leaf count and (2) the doubling constraint.'
  half_one_leaf_count: 'FAILS, 2 of 4. s1 and s3 return exactly two leaves. s0 returns THREE (two
    opposite plus one drooping lower leaf) and s2 returns THREE (one opposite pair plus a tall apical
    leaf). A plate that returns three leaves half the time is not a plate for a beat where the plant is
    the entire shot -- so the sample verdict is FAIL-COUNT.'
  half_two_scale: 'BINDS, and this is the large positive result of the whole pass. `no taller than the
    grass around it` holds on 3 of 4. s1 and s3 sit clearly BELOW the surrounding grass line, with the
    grass silhouetted against the sky well above the plant. s0 is level with the flanking blades. Only
    s2 overtops the grass. NOTHING doubled in size, nothing came back waist-high, nothing came back
    tree-sized -- the three failure modes the founder actually named for height did not occur. The
    height half of his ruling survives its first contact with the renderer.'
  not_scored: 'Cotyledon SHAPE was not judged: THE-SAPLING.md 2.2 flags round/oval as steward inference
    and vetoable in one line, so shape is not a fail axis. Leaf tilt is the motion job''s bar. No fig is
    asked for in this draft, so colour does not arise.'
  bar_looseness_scored_as_written: 'Two PASS clauses in this bar went UNMET on all four frames and are
    reported rather than used to fail the sample any harder: there is no TREELINE in any frame (the
    horizon is grass against sky), and no thin bare SIDE-BRANCH on any plant. Read strictly and
    conjunctively, 0 of 4 clear every clause. Read as the bar''s own "failure worth reporting" sentence
    frames it -- count and height -- the split is count-fails/height-binds. Both readings are given
    because the bar does not say which it means, and it is NOT being bent after the fact in either
    direction. Tighten it FORWARD: the next rung must state a RATE (how many of N) and must say whether
    treeline and side-branch are PASS requirements or scene-dressing.'
  filed_off_this: 'NOTHING. Beat 21 gets no motion seeds: at a 50 percent leaf-count defect the seeds
    could not pay off, because on this beat the sapling IS the shot. The wording lever to move next is
    leaf count alone -- the height clause should be carried forward UNCHANGED, since it is the one thing
    here that demonstrably works.'
""",
}


def main():
    changed = []
    for task, block in VERDICTS.items():
        path = os.path.join(JOBS, task + ".yaml")
        raw = open(path, encoding="utf-8").read()
        before_sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        before_keys = yaml.safe_load(raw)
        if "verdict_0817" in before_keys:
            sys.exit("!! %s already carries verdict_0817 -- refusing to double-append" % task)

        ins = block if raw.endswith("\n") else "\n" + block
        new = raw + ins
        # byte delta must be EXACTLY the inserted text
        assert len(new) - len(raw) == len(ins), task
        open(os.path.join(BAK, task + ".yaml.bak-0817"), "w", encoding="utf-8", newline="\n").write(raw)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(new)

        after_raw = open(path, encoding="utf-8").read()
        after_sha = hashlib.sha256(after_raw.encode("utf-8")).hexdigest()
        assert len(after_raw) - len(raw) == len(ins), task
        after_keys = yaml.safe_load(after_raw)

        added = set(after_keys) - set(before_keys)
        removed = set(before_keys) - set(after_keys)
        changed_keys = [k for k in before_keys if after_keys.get(k) != before_keys[k]]
        assert added == {"verdict_0817"}, (task, added)
        assert not removed, (task, removed)
        assert not changed_keys, (task, changed_keys)
        assert isinstance(after_keys["verdict_0817"], dict), task
        assert after_keys["verdict_0817"]["verdict"], task

        changed.append(task)
        print("%s\n  sha %s -> %s\n  +%d bytes, keys added %s, keys changed 0, verdict=%s"
              % (task, before_sha[:12], after_sha[:12], len(ins),
                 sorted(added), after_keys["verdict_0817"]["verdict"]))
    print("\n%d of 6 specs carry their verdict." % len(changed))


if __name__ == "__main__":
    main()
