#!/usr/bin/env python3
"""RUNG 4 on beat 15: the rooting clause loses every ground-material noun.

ONE VARIABLE, and it is the sentence rung 3 added. Same init, same sha, same
anchor, same seed 20260820, same negative byte for byte, same every flag, same
121 frames. Rung 3 is the control and it is an exact one.

WHY THIS RUNG EXISTS -- the noun law, three confirmations on one beat:

  rung 1  `talks to them from a HAND'S WIDTH away`      -> a hand arrived,
                                                           holding the plant
  rung 2  `Nobody touches the plant and nobody PICKS     -> a pick-up arrived:
           IT UP.`                                         the plant uprooted
                                                           in his fist at f120
  rung 3  `rising up out of the grass beside him with    -> A MOUND OF BARE
           SOIL and grass around its base`                  SOIL arrived, in
                                                           the frame's largest
                                                           object slot, which
                                                           was the goblin

At f094 of rung 3 the goblin is DELETED and replaced by a mound of earth in one
frame pair -- whole-frame interframe 28.14 against a clip median of 0.171 -- and
never returns. `soil` appears in no other beat-15 prompt: not listenmotion, not
listenlast. A noun is a placement wherever it appears, including inside a
subordinate clause describing something else, and a placement with no assigned
position takes the position of the largest thing nearby.

THE EDIT, stated as the diff it is. Rung 3's added sentence reads

    The plant's thin stem stays in the ground for the whole shot, rising up out
    of the grass beside him with soil and grass around its base, and it is
    rooted there in the last frame just as it is in the first.

and rung 4's reads

    The plant's thin stem stays in the grass for the whole shot, rising up out
    of the grass beside him with grass around its base, and it is rooted there
    in the last frame just as it is in the first.

Two words removed (`ground` -> `grass`, and `soil and ` deleted) and nothing
added. Every other character of the prompt -- all 1185 of rung 3's, minus those
-- is untouched. `grass` is not a neutral substitute chosen for tidiness: it is
the one material noun already saturating this plate and this prompt, so placing
it at the stem's base gives that slot a noun with nothing left to displace.

WHAT IS DELIBERATELY *NOT* EDITED, AND WHY IT IS NOT A HALF-MEASURE.
Rung 2's terminal sentence still contains `the plant is still rooted in the
GROUND with its stem rising out of the grass beside him`, and it stays byte for
byte. That is not an oversight and not a compromise -- it is the control:

  * `in the ground` was in rung 2's prompt as well, and RUNG 2 PRODUCED NO
    MOUND. It lost its plant to a fist, not to a substance. So the two nouns are
    already discriminated by measurement on this exact init at this exact seed,
    and only `soil` is indicted.
  * That sentence is the single most valuable clause in this family. It is the
    ongoing-action terminal placement that bought position for FREE -- FREEZE
    none, HOLD strength 0.508, the loosest of all six clips -- where its beat-03
    and beat-13 siblings paid a 33-frame dead tail for the same position. Editing
    it to chase a noun the evidence exonerates would put the one thing that works
    at risk to test a hypothesis rung 2 already answered.
  * And it would be a SECOND VARIABLE. A rung 4 that removed both and passed
    could not say which removal did it.

If a mound arrives anyway, `in the ground` is the last remaining ground noun in
the prompt and its deletion is rung 5 -- pre-registered below as
F-GROUND-IS-A-NOUN-TOO so that outcome is a finding and not a surprise.

ONE BAR CLAUSE IS ADDED, AND IT IS ADDED BECAUSE RUNG 3 EXPOSED A HOLE.
Rung 3's H1 -- is the plant still rooted in the last frame -- PASSED, and the
pass was worthless: the plant was rooted because the character who could pick it
up had been deleted from the picture. No clause in that bar could see the
subject leave. H0 below closes it, and it is written first because it gates
every other clause: if the goblin is not in every frame, nothing else is scored.
`a bar written on the target cannot see the code missing the target.`

H2 also gains an explicit VOID condition. judge_clip's HOLD/FREEZE statistics
are a performance reading only while the clip is ONE CONTINUOUS SHOT; rung 3
read HOLD period 1 / strength 0.01 -- nominally the best number in the family --
BECAUSE it contained a hard cut. The instrument is now told when it is broken.

$0. Writes ONE spec file and nothing else.
Run:  python3 pipeline/derive_b15_soilless_r4_0820.py [--force]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20260820

PARENT = "pipeline/jobs/ep2-b15-listenroot-0820.yaml"
NEW_ID = "ep2-b15-listengrass-0820"
OLD_BASE = "15-good-listener-LTX-rooted-0820"
NEW_BASE = "15-good-listener-LTX-grassroot-0820"
OLD_BENCH = "bench-b15-listenroot"
NEW_BENCH = "bench-b15-listengrass"

BEFORE = ("The plant's thin stem stays in the ground for the whole shot, rising "
          "up out of the grass beside him with soil and grass around its base, "
          "and it is rooted there in the last frame just as it is in the first.")
AFTER = ("The plant's thin stem stays in the grass for the whole shot, rising "
         "up out of the grass beside him with grass around its base, and it is "
         "rooted there in the last frame just as it is in the first.")

# Every ground-material noun this lane can think of, checked against the WHOLE
# rung-4 rooting clause after the edit. A regex over the whole prompt would fire
# on rung 2's deliberately-retained `in the ground`, which is the control; this
# checks the clause the rung owns.
GROUND_NOUNS = ("soil", "earth", "dirt", "mud", "loam", "clay", "ground",
                "topsoil", "humus", "compost", "sand", "gravel", "mound")

VARIABLE = (
    "THE ROOTING CLAUSE RUNG 3 ADDED, AND NOTHING ELSE. Two words go and none "
    "arrive: `stays in the ground` becomes `stays in the grass`, and `with soil "
    "and grass around its base` becomes `with grass around its base`. The clause "
    "keeps everything it was written to carry -- the stem's POSITION (beside "
    "him, out of the grass), its ROOTEDNESS, and the first-frame/last-frame "
    "continuity -- and carries ZERO ground-material nouns: no soil, no earth, no "
    "dirt, no mud, no loam, no ground. Rung 3's mound of bare earth occupied the "
    "frame's largest object slot, which was the goblin; `grass` is the one "
    "material already saturating this plate, so the base region gets a noun with "
    "nothing to displace. RUNG 2'S TERMINAL SENTENCE IS UNTOUCHED, INCLUDING ITS "
    "OWN `rooted in the ground` -- that phrase was in rung 2, rung 2 produced no "
    "mound, and editing the one clause in this family that bought position for "
    "free would be a second variable AND a risk to the only thing that works.")

RUNG_3_CONTROL = (
    "ep2-b15-listenroot-0820: FAIL, and the worst single frame this beat has "
    "produced. AT f094 THE GOBLIN IS DELETED AND REPLACED BY A MOUND OF BARE "
    "EARTH in ONE frame pair -- whole-frame interframe 28.14 against a clip "
    "median of 0.171, no other pair above 1.7, a hard swap and not a dissolve -- "
    "and he never comes back. The last 27 frames of a five-second beat about a "
    "man talking to a seedling contain no man. H1 passed on the letter and the "
    "pass was worthless: the plant is rooted because nobody is left to pick it "
    "up. H2 and the skin probe were both RETRACTED as broken by the defect they "
    "were pointed at -- a hold statistic reads a cut as stillness, and a fixed "
    "box on an empty frame reads luma 203 with luma_std 3.1. Rooted to f120, "
    "seated and talking at f030/f060/f090, camera locked.")

BAR = {
    "H0_THE_GOBLIN_IS_IN_EVERY_ONE_OF_THE_121_FRAMES": (
        "THE GATE. This clause did not exist before rung 3 and rung 3 is why it "
        "does: its bar had no way to notice that the subject had been deleted, "
        "and scored a PASS on the plant *because* he was gone. Instrument, "
        "pre-registered: whole-frame mean-absolute interframe luma over all 120 "
        "pairs must have NO pair above 8x the clip median (rung 3 read 28.14 "
        "against a median of 0.171, i.e. 165x), AND the goblin must be present "
        "and recognisable by eye at f000, f030, f060, f090, f094, f105 and f120 "
        "-- f094 named explicitly because that is the frame rung 3 died on. IF "
        "H0 FAILS, NOTHING ELSE IN THIS BAR IS SCORED: every other clause is "
        "measured on a shot that contains its subject, and a clause that can "
        "pass on an empty frame is not an instrument."),
    "H1_THE_PLANT_IS_STILL_ROOTED_IN_THE_LAST_FRAME": (
        "CARRIED VERBATIM FROM RUNG 3, and now gated by H0 so it cannot be won "
        "the way rung 3 won it. At f105 and f120, read at 2x on the plant "
        "region: the stem runs down into the grass and no hand is on it. Rung 2 "
        "is the precise control -- it passed this at f090 and failed it at f105 "
        "-- so the whole question is still the last sixth of the clip. A clip "
        "that holds to f090 and loses it again is a FAIL and the finding would "
        "be that the pick-up is not prompt-driven at all but something the "
        "engine does to a small object near a hand, after which the next rung is "
        "mechanical."),
    "H2_NOTHING_IS_BOUGHT_FROM_THE_PERFORMANCE": (
        "Rung 2's own numbers are the floor, because rung 2 is the control and "
        "it cost nothing: FREEZE none, and HOLD strength at or below 0.60 (rung "
        "2 read 0.508; its frozen beat-03 sibling read 0.958 with a 33-frame "
        "dead tail). A rung 4 that fixes the plant by stilling the clip has "
        "traded the one clean result in this family for the one broken clause, "
        "and is a FAIL. VOID CONDITION, ADDED AFTER RUNG 3 AND NOT NEGOTIABLE: "
        "judge_clip's HOLD and FREEZE statistics are a performance reading ONLY "
        "while the clip is one continuous shot. Rung 3 read HOLD period 1 / "
        "strength 0.01 -- nominally the loosest number this family has ever "
        "produced -- because it contained a hard cut, and every other clip in "
        "the family reads period 3 at 8.0 effective fps. If H0 fails, or if the "
        "clip reads period 1 while its siblings read period 3, this clause is "
        "RETRACTED AND NOT SCORED rather than credited."),
    "H3_the_beat_still_reads_and_he_stays_seated": (
        "Carried from rung 2, which passed both, and from rung 3, which passed "
        "it for 93 frames and then had no subject: he is sitting in the grass at "
        "f120, and his mouth is open and moving at f030/f060/f090. A regression "
        "on either is attributable to the one clause."),
}

FAIL_MODES = [
    "F-GROUND-IS-A-NOUN-TOO -- a mound of earth arrives anyway, from rung 2's "
    "surviving `the plant is still rooted in the GROUND`. That is the one "
    "ground-material noun this rung deliberately did not remove, on the evidence "
    "that rung 2 contained it and produced no mound. If it fires, the noun law "
    "is stronger than the rung-2 control suggested -- an abstract locative "
    "`ground` places a substance as readily as a material `soil` does -- and "
    "rung 5 is its deletion, which is then the LAST ground noun in the prompt "
    "and closes the axis. Named as the most likely FAIL of this rung.",
    "F-PLANT-PICKED-UP -- rung 2's defect returns. Rung 3 cannot be read on this "
    "clause at all: it kept its plant by deleting the hand's owner, so this rung "
    "is the FIRST clip to test the rooting clause against a goblin who is still "
    "in the picture. A pick-up here would mean the rooting clause never fixed "
    "anything and rung 3's H1 pass was pure artifact.",
    "F-STILL-FROZEN / F-STILL-DAMPED -- the clip buys the plant by stilling, "
    "i.e. beat 15 acquires the cost its beat-03 and beat-13 siblings pay. Scored "
    "against rung 2's 0.508, and only if H0 passes.",
    "F-SUBJECT-DELETED-AGAIN -- H0 fires. Whatever the cause, a second "
    "one-frame subject swap on this init at this seed makes it a property of the "
    "init and the recipe rather than of any word, and the next rung is "
    "mechanical rather than lexical.",
    "F-IDENTITY-DRIFT -- held on every clip in this family that still had a "
    "subject to measure; a regression would be attributable to the clause.",
    "F-MOUND-WITHOUT-DELETION -- a soil mound appears somewhere in frame while "
    "the goblin stays. Recorded separately from H0 because it would mean the "
    "noun places a substance but does not necessarily evict the largest object, "
    "which narrows the law's second half.",
]

NOT_DONE = (
    "NO recipe change -- size, frames, fps, guidance, distilled sigmas, "
    "two-stage, offload, mode and --image-crf 10 are the b14 crf-10 parent's, "
    "four rungs deep now. NO new init, NO new sha, NO new anchor. NO new seed: "
    "20260820 for the fourth time, so rungs 1, 2 and 3 are all true controls, "
    "and this box has already demonstrated bit-exact reproducibility across an "
    "eight-hour gap on this exact recipe. NO change to the NEGATIVE, unchanged "
    "since rung 1. NO SHORTER RENDER: --frames is an input to the denoiser's "
    "temporal grid and not a crop, so a shorter rung is a re-roll of the whole "
    "video and cannot inherit this one's early frames as evidence. NO edit to "
    "rung 2's terminal sentence, for the reason set out in the_one_variable. No "
    "pick, no plate_ack, no cut, no publication -- beat 15 stays a SLATE.")


def main():
    force = "--force" in sys.argv
    parent = derive_spec.load(os.path.join(REPO, PARENT))
    key = [k for k in parent["payload"]
           if k.endswith("b15-motion-prompt.txt")][0]
    old_prompt = parent["payload"][key]
    if BEFORE not in old_prompt:
        raise SystemExit("!! the clause to replace is not in the parent prompt -- "
                         "refusing to write a spec whose 'one variable' matched "
                         "nothing.")
    new_prompt = old_prompt.replace(BEFORE, AFTER, 1)

    # ---- the assertion this whole rung is: the clause carries no ground noun.
    low = AFTER.lower()
    hit = [n for n in GROUND_NOUNS if n in low]
    if hit:
        raise SystemExit("!! the rung-4 rooting clause still carries %s -- that "
                         "is the one thing this rung exists to remove. REFUSING."
                         % ", ".join(hit))
    # ---- and nothing was added: rung 4's prompt must be rung 3's minus words.
    if len(new_prompt) >= len(old_prompt):
        raise SystemExit("!! the rung-4 prompt is not shorter than rung 3's "
                         "(%d -> %d). This rung is a deletion; anything that "
                         "grows it is a second variable. REFUSING."
                         % (len(old_prompt), len(new_prompt)))
    removed = len(old_prompt) - len(new_prompt)

    child = derive_spec.derive(
        src=PARENT, new_id=NEW_ID,
        by="pipeline/derive_b15_soilless_r4_0820.py",
        fresh=dict(
            owner="the composite-plate motion lane, 2026-08-20, rung 4",
            consumer=(
                "The episode 2 cut, beat 15, still a SLATE. Rung 3 repaired the "
                "rooting clause and destroyed the beat doing it; this removes "
                "the noun that did the destroying and nothing else. Downstream: "
                "the beat's entry in review/ep2-picks/ and, if it passes, a "
                "founder screening. The cut swap is a taste call and is not "
                "proposed here."),
            success=(
                "ONE 704x1280 121-frame mp4 off the same init and the same seed "
                "as ep2-b15-listenroot-0820.yaml, differing from it in TWO "
                "DELETED WORDS inside one clause and in nothing else, in which "
                "the GOBLIN IS PRESENT IN ALL 121 FRAMES and the plant is still "
                "rooted at f120. %s Rung 3 is the control and the comparison is "
                "frame for frame against it: same init, same sha, same anchor, "
                "same seed, same negative byte for byte, same every flag, so a "
                "difference between them was bought by those two words."
                % VARIABLE),
            why=(
                "$0, ~4.5 minutes of GPU, no download. Beat 15 has now paid "
                "three GPU fires to learn one rule and the rule has three "
                "independent confirmations at one init and one seed: a noun is a "
                "placement wherever it appears, and an unplaced one takes the "
                "position of the largest thing nearby. Rung 4 is the cheapest "
                "possible test of that rule -- it deletes two words and adds "
                "none -- and it is also the first clip in this beat's history "
                "that can test the rooting clause against a goblin who is still "
                "in the picture, because rung 3 kept its plant by removing him. "
                "A bad result is attributable to the clause, and the most likely "
                "bad result is named."),
        ),
        overrides={"payload:b15-motion-prompt.txt": new_prompt, "seed": SEED},
        retoken=[(os.path.basename(PARENT)[:-5], NEW_ID),
                 (OLD_BASE, NEW_BASE),
                 (OLD_BENCH, NEW_BENCH)],
        extra={
            "skin_probe": _probe(parent),
            "rung_3_the_control": RUNG_3_CONTROL,
            "the_one_variable": VARIABLE,
            "bar": BAR,
            "not_done_on_purpose": NOT_DONE,
            "pre_registered_fail_modes": FAIL_MODES,
            "the_prompt_diff": {
                "parent_chars": len(old_prompt),
                "child_chars": len(new_prompt),
                "chars_removed": removed,
                "chars_added": 0,
                "before": BEFORE,
                "after": AFTER,
                "ground_nouns_checked_against_the_new_clause": list(GROUND_NOUNS),
                "deliberately_retained_elsewhere": (
                    "rung 2's terminal sentence `the plant is still rooted in "
                    "the ground with its stem rising out of the grass beside "
                    "him` -- byte for byte, as the control. See "
                    "the_one_variable and F-GROUND-IS-A-NOUN-TOO."),
            },
        })
    out = os.path.join("pipeline", "jobs", "%s.yaml" % NEW_ID)
    print("prompt %d -> %d chars (%d removed, 0 added)"
          % (len(old_prompt), len(new_prompt), removed))
    print(derive_spec.write(child, out, force=force))
    return 0


def _probe(parent):
    probe = dict(parent["skin_probe"])
    probe["carried_verbatim_from"] = (
        "ep2-b15-listenroot-0820.yaml, and through it from the rung-1 spec where "
        "the box was placed by eye at 5x before any of these frames existed. "
        "Every rung renders the same init at the same sha, anchor and 704x1280 "
        "crop, so the box lands on the same skin. Copied byte for byte and "
        "labelled rather than re-placed: re-placing a probe after the frames "
        "exist is choosing the number.")
    probe["retracted_on_rung_3_and_why"] = (
        "Rung 3's reading of this box -- f120 luma 203.2, R-B 93.9, nominally a "
        "+112.9 identity catastrophe -- WAS NOT AN IDENTITY READING. luma_std "
        "collapsed 14.9 -> 3.1: a flat box is an empty box, and this one was "
        "sitting on lit grass because the subject was out of the picture "
        "entirely. PUBLISH luma_std WITH EVERY READING. A collapse means the box "
        "is on a field and an EXPLOSION means it is on an edge (beat 13's went "
        "6.0 -> 85.0); both are the premise dying and only the dispersion shows "
        "it. If either shape appears, the probe is RETRACTED and re-placed by "
        "eye at 5x on the frame in question, and the verdict is written by eye "
        "at 1:1 against a re-placed box with material published beside luma.")
    return probe


if __name__ == "__main__":
    raise SystemExit(main())
