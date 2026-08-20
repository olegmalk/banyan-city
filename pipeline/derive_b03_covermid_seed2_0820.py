#!/usr/bin/env python3
"""THE SEED RE-ROLL on beat 03's rung 3. ONE VARIABLE: the seed. BARS UNCHANGED.

WHY A SEED AND NOT A WORDING RUNG. Rung 3 (`ep2-b03-covermid-0820`) missed its
own H1 BY ONE FRAME -- judge_clip FREEZE reads 7 frames dead from f114 against a
bar of "none, or a run shorter than 6" -- while buying, on the same clip, about
seventeen times the parent's motion energy through the middle (step-frame
whole-frame mean-absolute interframe luma f060..f072: rung 3 reads 7.60, 7.29,
7.02, 5.54, 7.20 where rung 2 reads 0.44, 0.40, 0.34, 0.05, 0.04). THE WORDING IS
EXONERATED BY THAT MEASUREMENT: the middle placement did what it was written to
do. What is left is a 7-frame tail run, and a 7-vs-6 miss is exactly the size of
thing a draw decides.

THE PRECEDENT IS ONE BEAT OVER AND ONE DAY OLD. `ep2-b15-listenmid-s2-0820`
changed only the seed on beat 15's rung 5 and separated the recipe from the draw
in 4.5 minutes: the motion was the RECIPE (it passed harder at the new seed) and
the temporal-resolution doubling was the DRAW. It also settled two earlier
single-seed losses -- rung 2's picked-up plant and rung 3's deleted goblin --
as properties of the WORDS and not of the draw. Beat 03 has the mirror question
and has never asked it: every one of its three rungs ran at seed 20260820.

WHAT THIS JOB CANNOT DO, said plainly so the report is not oversold. Beat 03's
live content ends at f073 (last pair with real movement f072->f073 at 7.199) and
the assembler's floor for this slot is VOICE-LED at 105 frames -- `fit_duration`
returns max(min(cdur, vdur+2.0), vdur+0.4) on a 3.982 s VO. A seed cannot buy
32 frames of performance. It can only answer whether the 7-frame EXACT run at
the tail is reproducible, and that answer decides whether the next lever is the
shorten-the-render candidate the rung-3 record already names or nothing at all.

BARS CARRIED FORWARD UNCHANGED, AND SAID OUT LOUD. `bar` is authored here
byte-identical to rung 3's H1-H4, so derive_spec records it as
`carried_verbatim_by_the_callers_own_hand` rather than letting it look
re-derived. Changing a bar between a clip and its confirmation seed is how a
confirmation becomes a selection. H2's height sub-clause is carried WITH the
note that the record has retired it (the VO of this beat is the sapling saying
"I am forty centimeters tall", and beats."03".done_when says a crouch that
actually conceals him FAILS) -- carried, not silently rewritten, because
retiring a clause inside a seed re-roll would change two variables.

$0, ~12 minutes, one 704x1280 121-frame mp4. Writes ONE spec file and nothing else.
Run:  python3 pipeline/derive_b03_covermid_seed2_0820.py [--force]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b03-covermid-0820.yaml"
NEW_ID = "ep2-b03-covermid-s2-0820"
OLD_BASE = "03-bad-cover-LTX-midend-0820"
NEW_BASE = "03-bad-cover-LTX-midend-s20260821-0820"
OLD_BENCH = "bench-b03-covermid"
NEW_BENCH = "bench-b03-covermid-s2"
SEED = 20260821

VARIABLE = (
    "THE SEED, 20260820 -> 20260821, AND NOTHING ELSE IN THE FILE. The prompt is "
    "rung 3's byte for byte -- including the HALFWAY THROUGH THE SHOT sentence "
    "and the terminal ongoing-action placement -- and so are the negative, the "
    "init, its sha, the 704x1280 crop, the anchor, 121 frames, guidance 2.0, "
    "distilled sigmas, two-stage, sequential offload and --image-crf 10. "
    "20260821 is the next integer after the seed all three of this beat's rungs "
    "have run on, chosen for that reason and no other, and it is the same seed "
    "beat 15's confirmation used: a neighbouring integer has no more claim on a "
    "good draw than a distant one, and picking a seed with a story attached is "
    "how a re-roll becomes a selection.")

H2_NOTE = (
    "H2 IS CARRIED WITH A KNOWN DEAD SUB-CLAUSE AND IS NOT REWRITTEN HERE. Its "
    "`shoulders no higher than the leaf tops` was RETIRED by the record on "
    "2026-08-20 as contradicting the beat it scores: this beat's VO is the "
    "sapling saying \"I am forty centimeters tall\", and beats.\"03\".done_when "
    "says a crouch that actually conceals him FAILS. Rung 3 measured the gap "
    "honestly -- leaf pair at y~800-850, top of his cloaked back at y~610 -- and "
    "no wording puts a grown goblin's back below a 15 cm plant. It stays in the "
    "text because editing a bar inside a seed re-roll changes two variables. "
    "SCORE H2 ON POSITION (in frame, down in the grass, behind the plant at "
    "f120) and report the height reading as a number without passing or failing "
    "the clip on it.")

EXTRA_CLAUSES = {
    "S5_THE_MIDDLE_IS_NOT_GIVEN_BACK": (
        "THE CLAUSE THAT PROTECTS WHAT RUNG 3 ACTUALLY WON, and it is measured "
        "on a floor calibrated against this beat's own history rather than "
        "invented. Step-frame whole-frame mean-absolute interframe luma across "
        "f060..f072 (this family holds every 3rd frame, 8.0 effective fps, all "
        "six clips) must average at or above 3.5. Rung 3 reads 7.60 / 7.29 / "
        "7.02 / 5.54 / 7.20 there and rung 2 reads 0.44 / 0.40 / 0.34 / 0.05 / "
        "0.04, so the floor is roughly HALF of rung 3 and eight times rung 2: a "
        "draw that halves the effect still passes and a draw that lands back in "
        "the terminal-placement regime cannot. H1 alone would let a clip that "
        "unfroze the tail by killing the middle read as an improvement."),
    "S6_THE_PLANT_AND_THE_RATIFIED_ADULT_BOTH_HOLD": (
        "GATE. If either fails nothing else is scored. The plant ONE thin stem "
        "and TWO leaves, rooted, no hand on it, at f000 f030 f060 f090 f120 "
        "(rung 3 passed this on the composite for the third rung running). The "
        "subject the ratified ADULT goblin -- lean wiry man, green skin, bald, "
        "long pointed ears, patchwork cloak -- present and recognisable in all "
        "121 frames, checked on a full-clip sheet. NOT a chibi child and NOT "
        "holding a leafy tree: that pair is the exact defect of the clip "
        "currently in the published cut, and it is what this composite route "
        "was built to close."),
    "S7_REPORT_WHERE_THE_CLIP_DIES_WHATEVER_IT_IS": (
        "NOT A PASS/FAIL CLAUSE -- the number this job is most likely to be "
        "remembered for. Publish the last frame pair whose whole-frame "
        "mean-absolute interframe luma exceeds 1.0. Rung 3 dies at f073 (7.199, "
        "then 0.012-0.155 to the end) and rung 2 died at f069, i.e. at "
        "essentially the same place regardless of the words. If the seed does "
        "not move it either, the death point is a property of the RECIPE or the "
        "LENGTH and the only remaining lever on this beat is the shorten-the-"
        "render candidate rung 3's record already names. If it does move it, "
        "that is a new axis and it was bought for $0."),
    "S8_identity_and_the_flat_box_lesson": (
        "Re-measure the skin probe box on f000 and f120 and publish R, G, B, R-B "
        "AND luma_std for both. Rung 3's pre-registered box was RETRACTED AS "
        "SCORED at this exact step: by f060 his head has dropped ~450 px and the "
        "box was sitting on the hazy horizon, reading a nominal +130 luma that "
        "was not an identity reading at all -- the tell was luma_std 18.5 -> 5.9. "
        "A FLAT BOX IS AN EMPTY BOX. If the box empties again, re-place by eye "
        "at 5x on f120 and say so, exactly as rung 3 did."),
}

FAIL_MODES = [
    "F-FREEZE-IS-THE-RECIPE -- H1 fails again at roughly 7 frames from roughly "
    "f114. NAMED AS THE MOST LIKELY OUTCOME AND THE REASONING IS PUBLISHED "
    "BEFORE THE PIXELS: rung 2 and rung 3 both die within four frames of each "
    "other from completely different terminal wordings, which is already two "
    "independent votes that the tail belongs to the recipe. If this fires, the "
    "wording axis AND the seed axis are both closed on beat 03 and the honest "
    "next step is the 73-frame render (no dead tail to fill, 40% less GPU) or "
    "nothing.",
    "F-THE-MIDDLE-WAS-THE-DRAW -- S5 fails: the f060..f072 band collapses toward "
    "rung 2's numbers with the wording untouched. This would be the most "
    "valuable failure in the set and it would contradict beat 15, where the "
    "same edit's motion passed HARDER at this same seed. It would mean rung 3's "
    "central finding -- that a middle in continuous aspect buys motion -- rests "
    "on one draw on two beats, and every conclusion drawn from it would need "
    "re-reading.",
    "F-PLANT-PICKED-UP / F-SUBJECT-SWAPPED at a new seed -- S6's gate. Beat 15 "
    "answered the sibling version of this NO (neither rung 2's picked-up plant "
    "nor rung 3's deleted goblin returned at 20260821), so a hit here would say "
    "the composite init's protection is weaker on beat 03 than on beat 15.",
    "F-DEATH-POINT-MOVES -- S7's number lands materially away from f073. Not a "
    "failure of the beat; a sharpening. It would be the first evidence on this "
    "beat that anything other than the length controls where the performance "
    "stops.",
    "F-H1-PASSES-AND-NOTHING-ELSE-CHANGES -- the run comes back at 5 frames or "
    "fewer and the clip is otherwise indistinguishable. THIS IS A PASS THAT MUST "
    "NOT BE OVERSOLD: a 7-vs-5 difference at the tail is a draw crossing a "
    "threshold, not a repair, and the 32 near-dead frames between f073 and f105 "
    "are untouched by it. Say so in the verdict rather than reporting a green "
    "H1 as a fixed beat.",
]

NOT_DONE = (
    "NO WORDING CHANGE OF ANY KIND -- rung 3's measurement exonerated the "
    "wording and this job would destroy that control. NO BAR CHANGE: H1-H4 are "
    "carried byte-identical and the four clauses added here are additions, not "
    "edits, every one of them calibrated against a number this beat has already "
    "produced. NO SHORTER RENDER -- 121 frames stays, because --frames is an "
    "input to the denoiser's temporal grid and not a crop, and testing it is a "
    "different rung with a different control. NO TRIM AND NO SIDECAR: both trim "
    "points were computed on rung 3 and both were refused in writing (f073 "
    "re-adds a 1.299 s hold with 0.60 s of the line over a frozen picture; f105 "
    "is a trim chosen to satisfy an instrument). NO PLATE WORK and no new init, "
    "sha, anchor or mask. NO THIRD SEED FILED ALONGSIDE THIS ONE -- if this "
    "agrees with rung 3 the question is closed at two, exactly as beat 15's was. "
    "AND NO CUT SWAP IS PROPOSED BY THIS SPEC: whether rung 3 or this seed sits "
    "in review/ep2-demo-0820's beat 03 slot is an assembly decision made "
    "elsewhere, and this file neither makes it nor pre-writes it."
)


def main():
    force = "--force" in sys.argv
    parent = derive_spec.load(os.path.join(REPO, PARENT))
    pkey = [k for k in parent["payload"] if k.endswith("b03-motion-prompt.txt")][0]
    prompt = parent["payload"][pkey]
    bar = dict(parent["bar"])

    child = derive_spec.derive(
        src=PARENT, new_id=NEW_ID,
        by="pipeline/derive_b03_covermid_seed2_0820.py",
        fresh=dict(
            owner="the composite-plate motion lane, 2026-08-20, the beat 03 seed re-roll",
            consumer=(
                "The episode 2 cut, beat 03, which is NOT a slate -- it ships a "
                "clip of a chibi CHILD holding a leafy TREE, and rung 3 is the "
                "swap candidate that beats it on every measurable axis while "
                "failing its own H1 by one frame. This asks the only cheap "
                "question left before that swap is settled: is the 7-frame tail "
                "run the recipe or the draw. Downstream: the beat's row in "
                "review/ep2-demo-0820/sources/picks-0820.yaml and the assembly "
                "that reads it."),
            success=(
                "ONE 704x1280 121-frame mp4 off the SAME PROMPT, the same init "
                "and the same sha as ep2-b03-covermid-0820, at a DIFFERENT SEED, "
                "which either clears H1's 6-frame allowance or reproduces rung "
                "3's 7-frame run -- and which in EITHER case keeps the middle "
                "alive, the plant rooted and the ratified adult in all 121 "
                "frames, so that the answer is about the tail and about nothing "
                "else. %s" % VARIABLE),
            why=(
                "$0, ~12 minutes, and the miss is one frame wide. A bar of 6 and "
                "a reading of 7 is the smallest gap this lane has ever reported, "
                "and the cheapest possible test of whether it is real is the "
                "same one that worked on beat 15 yesterday for 4.5 minutes: "
                "change the draw and nothing else. Both outcomes are worth the "
                "card -- a pass promotes rung 3's recipe from one draw to two, "
                "and a repeat closes beat 03's seed axis and hands the beat to "
                "the author with one fewer open lever. Every wording lever on "
                "this beat is already closed by measurement, so this is the last "
                "$0 question it has."),
        ),
        overrides={"seed": SEED},
        retoken=[(os.path.basename(PARENT)[:-5], NEW_ID),
                 (OLD_BASE, NEW_BASE), (OLD_BENCH, NEW_BENCH)],
        extra=dict(
            {
                "skin_probe": dict(parent["skin_probe"]),
                "bar": bar,
                "the_bars_are_carried_unchanged_and_here_is_the_note_on_H2": H2_NOTE,
                "rung_3_the_control": (
                    "ep2-b03-covermid-0820 at seed 20260820, rc=0, 121 frames, "
                    "268.3 s, $0. judge_clip FREEZE 7 frames dead from f114 at "
                    "ncc 1.0000 (rung 2: 33 from f088). Step-frame interframe "
                    "f060..f072 7.60 / 7.29 / 7.02 / 5.54 / 7.20, then 0.07 and "
                    "below from f075 to the end; last pair above 1.0 is "
                    "f072->f073 at 7.199, so live content is 74 frames = "
                    "3.0833 s. Whole-frame ncc floor 0.9074 against a bar of "
                    "below 0.95. Plant held at all five checkpoints; the duck "
                    "reads and he is still crouched behind the plant at f120; "
                    "the cover is comically inadequate as the beat requires. "
                    "H2's height sub-clause missed by ~200 px and is retired."),
                "the_one_variable": VARIABLE,
                "not_done_on_purpose": NOT_DONE,
                "pre_registered_fail_modes": FAIL_MODES,
                "the_prompt_is_unchanged": {
                    "chars": len(prompt),
                    "asserted": "byte-identical to ep2-b03-covermid-0820's",
                },
                "what_a_seed_cannot_buy_on_this_beat": (
                    "STATED BEFORE THE RENDER SO THE REPORT IS NOT OVERSOLD. The "
                    "slot floor is voice-led: render_t3.fit_duration returns "
                    "max(min(cdur, vdur+2.0), vdur+0.4) and beat 03's VO is "
                    "total_s 3.982, so the slot is 4.382 s = 105 frames whatever "
                    "clip it is handed. Rung 3's live content is 74 frames. The "
                    "spoken line outruns the live footage by 0.9 s and a "
                    "different draw does not change that arithmetic -- the "
                    "hold-last-frame fill covers the difference either way. A "
                    "green H1 here means the EXACT-duplicate run at the tail got "
                    "shorter, not that the beat gained performance."),
            },
            **EXTRA_CLAUSES))

    out = os.path.join("pipeline", "jobs", "%s.yaml" % NEW_ID)
    ckey = [k for k in child["payload"] if k.endswith("b03-motion-prompt.txt")][0]
    if child["payload"][ckey] != prompt:
        raise SystemExit("!! the prompt changed. This job's only variable is the "
                         "seed. REFUSING.")
    if child["bar"] != parent["bar"]:
        raise SystemExit("!! the bar changed. Bars are carried forward unchanged "
                         "on a seed re-roll. REFUSING.")
    print("prompt unchanged, %d chars; bar unchanged, %d clauses; seed %d -> %d"
          % (len(prompt), len(bar), 20260820, SEED))
    print(derive_spec.write(child, out, force=force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
